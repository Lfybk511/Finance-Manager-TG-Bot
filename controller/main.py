"""Сервер Telegram бота, запускаемый непосредственно"""
import logging
import os
import aiohttp
# from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # Для машины состояний

from utils import exceptions
from utils import expenses
from utils.categories import Categories
import output_data
storage = MemoryStorage()

logging.basicConfig(level=logging.INFO)

API_TOKEN =
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.from_user.id == 478916678:
        buttons = ["/Сегодня", "/Месяц", "/Категории", "/Последние_расходы", "/Помощь", "/admin"]
    else:
        buttons = ["/Сегодня", "/Месяц", "/Категории", "/Последние_расходы", "/Помощь"]
    keyboard.add(*buttons)
    await message.answer("👋")
    await message.answer(f"❤️Давай начнем, {message.from_user.username}❤️", reply_markup=keyboard)
    await help(message)


@dp.message_handler(commands=['Помощь'])
async def help(message: types.Message):
    await message.answer(
        "💵 Бот для учёта ненужных трат 💵\n"
        "Предотвратит бесполезную трату денег\n\n"
        "✅ Отправляйте боту расходы, \nкоторые вы считаете бесполезными\n"
        "Он будет вести за вас статистику! \n\n"
        "✅ Инструкция:\n"
        "Чтобы добавить расход напишите сумму и категорию расхода\n"
        "Пример: 100 сладости\n\n"
        "✅ Чтобы узнать категории нажмите кнопку \n/Категории "
        "В скобках указаны слова, которые понимает бот. "
        "Если вашего слова нет в списке, то бот отнесёт трату в категорию 'Прочее'\n\n"
        "✅ Если необходимо удалить трату, нажмите\n"
        "/Последние_расходы Появится список из 10-ти последних операций\n\n"
        "✅ Присутствует важная категория 'Сохранил'\n"
        "Если не потратили деньги на бесполезную покупку: 100 сохранил\n\n"
        )


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_expense(message: types.Message):
    """Удаляет одну запись о расходе по её идентификатору"""
    row_id = int(message.text[4:])
    expenses.delete_expense(row_id, message.from_user.id)
    await message.answer("🔥")
    answer_message = "Удалил\n\n"
    await message.answer(answer_message)
    await today_statistics(message)


@dp.message_handler(commands=['Категории'])
async def categories_list(message: types.Message):
    """Отправляет список категорий расходов"""
    categories = Categories().get_all_categories()
    answer_message = "Категории трат:\n\n" +\
            ("\n\n ".join([c.name+' ('+", ".join(c.aliases)+')' for c in categories]))
    await message.answer(answer_message)


@dp.message_handler(commands=['Сегодня'])
async def today_statistics(message: types.Message):
    """Отправляет сегодняшнюю статистику трат"""
    today_expenses = expenses.get_today_statistics(message.from_user.id)
    #print(today_expenses)
    if today_expenses[0]:
        answer_message = "💵 Траты за сегодня:  " + "".join(f"{today_expenses[1].amount} руб. 💵")
        today_expenses_rows = [
            f"{expense.category_name[:1]}  {expense.amount}р  на {expense.category_name[1:]}"
            for expense in today_expenses[0]]
        answer_message += "\n\n" + "\n\n" \
            .join(today_expenses_rows)
    else:
        answer_message = "💵 Трат за сегодня нет 💵"

    if today_expenses[2].amount:
        answer_message += "\n\n ✅Вы сохранили: " + "".join(f"{today_expenses[2].amount} руб✅")
    await message.answer(answer_message)



@dp.message_handler(commands=['Месяц'])
async def month_statistics(message: types.Message):
    """Отправляет статистику трат текущего месяца"""
    month_expenses = expenses.get_month_statistics(message.from_user.id)
    if month_expenses[0]:
        answer_message = "💵 Траты за месяц:  " + "".join(f"{month_expenses[1].amount} руб. 💵")
        month_expenses_rows = [
            f"{expense.category_name[:1]}  {expense.amount}р  на {expense.category_name[1:]}"
            for expense in month_expenses[0]]
        answer_message += "\n\n" + "\n\n" \
            .join(month_expenses_rows)
    else:
        answer_message = "💵 Трат за месяц нет 💵"
    if month_expenses[2].amount:
        answer_message += "\n\n ✅Вы сохранили: " + "".join(f"{month_expenses[2].amount} руб✅")
    await message.answer(answer_message)


@dp.message_handler(commands=['Последние_расходы'])
async def list_expenses(message: types.Message):
    """Отправляет последние несколько записей о расходах"""
    last_expenses = expenses.last(message.from_user.id)
    if not last_expenses:
        await message.answer("Расходы ещё не заведены")
        return

    last_expenses_rows = [
        f"{expense.category_name[0:1]} {expense.amount}р  на {expense.category_name[1:]} — нажми "
        f"/del{expense.id} для удаления"
        for expense in last_expenses]
    answer_message = "Последние сохранённые траты:\n\n" + "\n\n"\
            .join(last_expenses_rows)
    await message.answer(answer_message)


# @dp.message_handler(commands=['Добавить_Категорию'])
# async def categories_list(message: types.Message):
#     """Отправляет список категорий расходов"""
#     if message.from_user.id != "478916678":
#         await message.answer("Введите пароль!")
#
#
#     categories = Categories().get_all_categories()
#     answer_message = "Категории трат:\n\n" +\
#             ("\n\n ".join([c.name+' ('+", ".join(c.aliases)+')' for c in categories]))
#     await message.answer(answer_message)


@dp.message_handler(commands=['admin'])
async def categories_list(message: types.Message):
    if message.from_user.id == 478916678:
        answer_message = "Режим Админа доступен\n\n"\
                         "Посмотреть количество зарегистированных пользователей: /users\n \n" \
                         "Общее количество записей: /count"
    else:
        answer_message = "Отказано в доступе!"
    await message.answer(answer_message)


@dp.message_handler(commands=['users'])
async def categories_list(message: types.Message):
    if message.from_user.id == 478916678:
        answer_message = "Зарегистрировано: " + expenses.Users()
    else:
        answer_message = "Отказано в доступе!"
    await message.answer(answer_message)


@dp.message_handler(commands=['count'])
async def categories_list(message: types.Message):
    if message.from_user.id == 478916678:
        answer_message = "Записей: " + expenses.Count()
    else:
        answer_message = "Отказано в доступе!"
    await message.answer(answer_message)


async def add_expense(message: types.Message):
    """Добавляет новый расход"""
    try:
        expense = expenses.add_expense(message.text, message.from_user.id)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    answer_message = (
        f"Добавлены траты {expense.amount} руб на {expense.category_name}.\n\n"
            )
        #f"{expenses.get_today_statistics(message.from_user.id)}\n"
    await message.answer(answer_message)
    await today_statistics(message)

def add_handlers_expence(dp: Dispatcher):
    dp.register_message_handler(add_expense)



@dp.message_handler(commands="random")
async def cmd_random(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Нажми меня", callback_data="count"))
    await message.answer("Нажмите на кнопку, чтобы бот отправил число от 1 до 10", reply_markup=keyboard)


@dp.callback_query_handler(text="random_value")
async def send_random_value(call: types.CallbackQuery):
    await call.message.answer('/users')



# @bot.message_handler(commands=['date'])
# def start(m):
#      calendar, step = DetailedTelegramCalendar().build()
#      bot.send_message(m.chat.id,
#          f"Select {LSTEP[step]}",
#          reply_markup=calendar)
#
#
# @bot.callback_query_handler(func=DetailedTelegramCalendar.func())
# def cal(c):
#      result, key, step = DetailedTelegramCalendar().process(c.data)
#      if not result and key:
#         bot.edit_message_text(f"Select {LSTEP[step]}",
#          c.message.chat.id,
#          c.message.message_id,
#          reply_markup=key)
#      elif result:
#          bot.edit_message_text(f"You selected {result}",
#              c.message.chat.id,
#              c.message.message_id)


if __name__ == '__main__':

    output_data.register_handlers_data(dp)
    add_handlers_expence(dp)
    executor.start_polling(dp, skip_updates=True)
