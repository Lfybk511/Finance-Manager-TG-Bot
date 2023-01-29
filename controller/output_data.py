from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from main import dp
from aiogram import Dispatcher


class FSMdate(StatesGroup):
    type = State()


#@dp.massage_handler(commands="Загрузить", state=None)
async def date_start(message: types.Message):
    await FSMdate.type.set()
    await message.reply("Назови дату")
    markup = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="-1", callback_data="num_decr"),
        types.InlineKeyboardButton(text="+1", callback_data="num_incr")]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    await message.reply( "Нажми на кнопку и перейди на наш сайт.", reply_markup=markup)


async def day_or_mouth(message: types.Message):
    await FSMdate.type.set()
    await message.reply("Назови даassasту")



#@dp.massage_handler(state=FSMdate.type)
async def load_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["type"] = message.text
    async with state.proxy() as data:
        await message.reply(str(data))
    await state.finish()


def register_handlers_data(dp: Dispatcher):
    dp.register_message_handler(date_start, commands="add", state=None)
    dp.register_message_handler(load_date, state=FSMdate.type)
