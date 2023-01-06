""" Работа с расходами — их добавление, удаление, статистики"""
import datetime
import re
from typing import List, NamedTuple, Optional

import pytz

from . import db
from . import exceptions
from .categories import Categories


class PrintCategories(NamedTuple):
    amount: int
    category_name: str


class Message(NamedTuple):
    """Структура распаршенного сообщения о новом расходе"""
    amount: int
    category_text: str


class Expense(NamedTuple):
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
    inserted_row_id = db.insert("expense", {

        "user_id": user_ID,
        "amount": parsed_message.amount,
        "created": _get_now_formatted(),
        "category_codename": category.codename,
        "raw_text": raw_message
    })
    return Expense(id=None,
                   user_id=user_ID,
                   amount=parsed_message.amount,
                   category_name=category.name)


def get_today_statistics(user_ID: int) -> List[PrintCategories]:
    """Возвращает строкой статистику расходов за сегодня"""
    cursor = db.get_cursor()
    result = []
    for cate in Categories().get_all_categories():
        #print(cate.codename)
        cursor.execute("select sum(amount) "
                       "from expense where date(created)=date('now', 'localtime') "
                       f"and user_id = {user_ID} "
                       f"and category_codename = '{cate.codename}' ")
        res = cursor.fetchone()
        #print("cursor.fetchone() ===== ",res[0])
        if res[0]:
            result.append(PrintCategories(amount=int(res[0]), category_name=cate.name))
    return sorted(result, key=lambda x: -x.amount)

    if not result[0]:
        return "Сегодня ещё нет расходов"
    all_today_expenses = result[0]
    #print(result)
    return (f"Расходы сегодня:\n"
            f"всего — {all_today_expenses} руб.\n\n"
            "Сегодняшняя статистика: /today\n"
            "За текущий месяц: /month\n"
            "Последние внесённые расходы: /expenses\n"
            "Категории трат: /categories")


def get_month_statistics(user_ID) -> str:
    """Возвращает строкой статистику расходов за текущий месяц"""
    now = _get_now_datetime()
    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
    cursor = db.get_cursor()
    result = []
    for cate in Categories().get_all_categories():
        #print(cate.codename)
        cursor.execute("select sum(amount) "
                       f"from expense where date(created) >= '{first_day_of_month}' "
                       f"and user_id = {user_ID} "
                       f"and category_codename = '{cate.codename}' ")
        res = cursor.fetchone()
        #print("cursor.fetchone() ===== ",res[0])
        if res[0]:
            result.append(PrintCategories(amount=int(res[0]), category_name=cate.name))
    return sorted(result, key=lambda x: -x.amount)

    if not result[0]:
        return "В этом месяце ещё нет расходов"
    all_today_expenses = result[0]
    return (f"Расходы в текущем месяце:\n"
            f"всего — {all_today_expenses} руб.\n\n"
            "Сегодняшняя статистика: /today\n"
            "За текущий месяц: /month\n"
            "Последние внесённые расходы: /expenses\n"
            "Категории трат: /categories")


def last(user_ID: int) -> List[Expense]:
    """Возвращает последние несколько расходов"""
    cursor = db.get_cursor()
    cursor.execute(
        "select e.user_id, e.id, e.amount, c.name "
        "from expense  e left join category c "
        f"on c.codename=e.category_codename where user_id = {user_ID}"
        " order by created desc limit 10 ")
    rows = cursor.fetchall()
    #print(rows)
    last_expenses = [Expense(user_id=row[0], id=row[1], amount=row[2], category_name=row[3]) for row in rows]
    return last_expenses


def delete_expense(row_id: int) -> None:
    """Удаляет сообщение по его идентификатору"""
    db.delete("expense", row_id)


def _parse_message(raw_message: str) -> Message:
    """Парсит текст пришедшего сообщения о новом расходе."""
    regexp_result = re.match(r"([\d ]+) (.*)", raw_message)
    if not regexp_result or not regexp_result.group(0) \
            or not regexp_result.group(1) or not regexp_result.group(2):
        raise exceptions.NotCorrectMessage(
            "Не могу понять сообщение. Напишите сообщение в формате, "
            "например:\n1500 метро")

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