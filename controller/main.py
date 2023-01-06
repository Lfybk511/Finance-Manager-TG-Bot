"""Сервер Telegram бота, запускаемый непосредственно"""
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher, executor, types

from utils import exceptions
from utils import expenses
from utils.categories import Categories


logging.basicConfig(level=logging.INFO)
# TELEGRAM_API_TOKEN

API_TOKEN = "5980027616:AAHqC1Ux43-Zw6REeNTAMZidYXqqa6WEMaE"
#TELEGRAM_API_TOKEN
# PROXY_URL = os.getenv("TELEGRAM_PROXY_URL")
# PROXY_AUTH = aiohttp.BasicAuth(
#     login=os.getenv("TELEGRAM_PROXY_LOGIN"),
#     password=os.getenv("TELEGRAM_PROXY_PASSWORD")
# )
# ACCESS_ID = os.getenv("TELEGRAM_ACCESS_ID")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
#dp.middleware.setup(AccessMiddleware(ACCESS_ID))


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение и помощь по боту"""
    await message.answer(
        "Бот для учёта ненужных трат\n"
        "Предотватит бесполезную трату денег\n\n"
        "Добавить расход: 250 сладости\n"
        "Если не потратили деньги на бесполезную покупку: 100 сохранил\n\n"
        "Категории трат: /categories\n"
        "Сегодняшняя статистика: /today\n"
        "За текущий месяц: /month\n"
        "Последние внесённые расходы: /expenses"
        )


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_expense(message: types.Message):
    """Удаляет одну запись о расходе по её идентификатору"""
    row_id = int(message.text[4:])
    expenses.delete_expense(row_id)
    answer_message = "Удалил"
    await message.answer(answer_message)


@dp.message_handler(commands=['categories'])
async def categories_list(message: types.Message):
    """Отправляет список категорий расходов"""
    categories = Categories().get_all_categories()
    answer_message = "Категории трат:\n\n* " +\
            ("\n* ".join([c.name+' ('+", ".join(c.aliases)+')' for c in categories]))
    await message.answer(answer_message)


@dp.message_handler(commands=['today'])
async def today_statistics(message: types.Message):
    """Отправляет сегодняшнюю статистику трат"""
    today_expenses = expenses.get_today_statistics(message.from_user.id)
    if not today_expenses:
        await message.answer("Расходы сегодня не заведены")
        return
    today_expenses_rows = [
        f"{expense.amount} руб. на {expense.category_name} "
        for expense in today_expenses]
    answer_message = "Траты за сегодня:\n\n* " + "\n\n* " \
        .join(today_expenses_rows)
    await message.answer(answer_message)



@dp.message_handler(commands=['month'])
async def month_statistics(message: types.Message):
    """Отправляет статистику трат текущего месяца"""
    month_expenses = expenses.get_today_statistics(message.from_user.id)
    if not month_expenses:
        await message.answer("Расходы за этот месяц не заведены")
        return
    month_expenses_rows = [
        f"{expense.amount} руб. на {expense.category_name} "
        for expense in month_expenses]
    answer_message = "Траты за месяц:\n\n* " + "\n\n* " \
        .join(month_expenses_rows)
    await message.answer(answer_message)


@dp.message_handler(commands=['expenses'])
async def list_expenses(message: types.Message):
    """Отправляет последние несколько записей о расходах"""
    last_expenses = expenses.last( message.from_user.id)
    if not last_expenses:
        await message.answer("Расходы ещё не заведены")
        return

    last_expenses_rows = [
        f"{expense.amount} руб. на {expense.category_name} — нажми "
        f"/del{expense.id} для удаления"
        for expense in last_expenses]
    answer_message = "Последние сохранённые траты:\n\n* " + "\n\n* "\
            .join(last_expenses_rows)
    await message.answer(answer_message)


@dp.message_handler()
async def add_expense(message: types.Message):
    """Добавляет новый расход"""
    try:
        expense = expenses.add_expense(message.text, message.from_user.id)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    answer_message = (
        f"Добавлены траты {expense.amount} руб на {expense.category_name}.\n\n"
        "Категории трат: /categories\n"
        "Сегодняшняя статистика: /today\n"
        "За текущий месяц: /month\n"
        "Последние внесённые расходы: /expenses"
            )
        #f"{expenses.get_today_statistics(message.from_user.id)}\n"
    await message.answer(answer_message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
