""" Работа с расходами — их добавление, удаление, статистики"""
import datetime
import re
from typing import List, NamedTuple, Optional
from dataclasses import dataclass
import pytz

from . import db
from . import exceptions
from .categories import Categories


@dataclass
class PrintCategories():
    amount: int
    category_name: str



@dataclass
class Message():
    """Структура распаршенного сообщения о новом расходе"""
    amount: int
    category_text: str


@dataclass
class Expense():
    """Структура добавленного в БД нового расхода"""
    user_id: int
    id: Optional[int]
    amount: int
    category_name: str


def add_expense(raw_message: str, user_ID: int) -> Expense:
    """Добавляет новое сообщение.
    Принимает на вход текст сообщения, пришедшего в бот."""
    parsed_message = _parse_message(raw_message)
    category = Categories().get_category(
        parsed_message.category_text)
    cursor = db.get_cursor()
    cursor.execute("select count() "
                   f"from expense where user_id = {user_ID} ")
    res = cursor.fetchone()
    inserted_row_id = db.insert("expense", {

        "user_id": user_ID,
        "del_id": res[0] + 1,
        "amount": parsed_message.amount,
        "created": _get_now_formatted(),
        "category_codename": category.codename,
        "raw_text": raw_message
    })
    return Expense(id=None,
                   user_id=user_ID,
                   amount=parsed_message.amount,
                   category_name=category.name)


def get_today_statistics(user_ID: int) -> List[List[PrintCategories]]:
    """Возвращает строкой статистику расходов за сегодня"""
    cursor = db.get_cursor()
    result = []
    for cate in Categories().get_all_categories()[1:]:
        cursor.execute("select sum(amount) "
                       "from expense where date(created)=date('now', 'localtime') "
                       f"and user_id = {user_ID} "
                       f"and category_codename = '{cate.codename}' ")
        res = cursor.fetchone()
        if res[0]:
            result.append(PrintCategories(amount=int(res[0]), category_name=cate.name))
            result = sorted(result, key=lambda x: -x.amount)
    if not len(result):
        result = 0
    ans = []
    ans.append(result)

    cursor.execute("select sum(amount) "
                   "from expense where date(created)=date('now', 'localtime') "
                   f"and user_id = {user_ID} "
                   "and category_codename != 'saved' ")
    res = cursor.fetchone()

    if res[0]:
        ans.append(PrintCategories(amount=int(res[0]), category_name="Sum"))
    else:
        ans.append(PrintCategories(amount=0, category_name="sum"))
    cursor.execute("select sum(amount) "
                   "from expense where date(created)=date('now', 'localtime') "
                   f"and user_id = {user_ID} "
                   "and category_codename = 'saved' ")
    res = cursor.fetchone()
    if res[0]:
        ans.append(PrintCategories(amount=int(res[0]), category_name="saved"))
    else:
        ans.append(PrintCategories(amount=0, category_name="saved"))

    return ans



def get_month_statistics(user_ID) -> str:
    """Возвращает строкой статистику расходов за текущий месяц"""
    now = _get_now_datetime()
    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
    cursor = db.get_cursor()
    result = []
    for cate in Categories().get_all_categories()[1:]:
        # print(cate.codename)
        cursor.execute("select sum(amount) "
                       f"from expense where date(created) >= '{first_day_of_month}' "
                       f"and user_id = {user_ID} "
                       f"and category_codename = '{cate.codename}' ")
        res = cursor.fetchone()
        if res[0]:
            result.append(PrintCategories(amount=int(res[0]), category_name=cate.name))
            result = sorted(result, key=lambda x: -x.amount)
    if not len(result):
        result = 0
    ans = []
    ans.append(result)

    cursor.execute("select sum(amount) "
                   f"from expense where date(created) >= '{first_day_of_month}' "
                   f"and user_id = {user_ID} "
                   "and category_codename != 'saved' ")
    res = cursor.fetchone()

    if res[0]:
        ans.append(PrintCategories(amount=int(res[0]), category_name="Sum"))
    else:
        ans.append(PrintCategories(amount=0, category_name="sum"))
    cursor.execute("select sum(amount) "
                   f"from expense where date(created) >= '{first_day_of_month}'  "
                   f"and user_id = {user_ID} "
                   "and category_codename = 'saved' ")
    res = cursor.fetchone()
    #print('res=    ',res)
    if res[0]:
        ans.append(PrintCategories(amount=int(res[0]), category_name="saved"))
    else:
        ans.append(PrintCategories(amount=0, category_name="saved"))

    return ans


def last(user_ID: int) -> List[Expense]:
    """Возвращает последние несколько расходов"""
    cursor = db.get_cursor()
    cursor.execute(
        "select e.user_id, e.del_id, e.amount, c.name "
        "from expense  e left join category c "
        f"on c.codename=e.category_codename where user_id = {user_ID}"
        " order by created desc limit 10 ")
    rows = cursor.fetchall()
    last_expenses = [Expense(user_id=row[0], id=row[1], amount=row[2], category_name=row[3]) for row in rows]
    return last_expenses


def Users():
    cursor = db.get_cursor()
    cursor.execute(
        "select count(DISTINCT user_id) "
        "from expense")
    rows = cursor.fetchone()
    return str(rows[0])


def Count():
    cursor = db.get_cursor()
    cursor.execute(
        "select count(id) "
        "from expense")
    rows = cursor.fetchone()
    return str(rows[0])


def delete_expense(row_id: int, user_id: int) -> None:
    """Удаляет сообщение по его идентификатору"""
    db.delete("expense", row_id, user_id)


def _parse_message(raw_message: str) -> Message:
    """Парсит текст пришедшего сообщения о новом расходе."""
    regexp_result = re.match(r"([\d ]+) (.*)", raw_message)
    if not regexp_result or not regexp_result.group(0) \
            or not regexp_result.group(1) or not regexp_result.group(2):
        raise exceptions.NotCorrectMessage(
            "❌ Не могу понять сообщение ❌\n\nНапишите сообщение в формате, "
            "например:\n1500 такси")

    amount = regexp_result.group(1).replace(" ", "")
    category_text = regexp_result.group(2).strip().lower()
    return Message(amount=amount, category_text=category_text)


def _get_now_formatted() -> str:
    """Возвращает сегодняшнюю дату строкой"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
    """Возвращает сегодняшний datetime с учётом времненной зоны Мск."""
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.datetime.now(tz)
    return now


def _get_budget_limit() -> int:
    """Возвращает дневной лимит трат для основных базовых трат"""
    return db.fetchall("budget", ["daily_limit"])[0]["daily_limit"]
