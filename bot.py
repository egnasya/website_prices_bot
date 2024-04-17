from aiogram import types, Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter, CommandStart, state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from my_token import TOKEN
from aiogram.fsm.state import default_state, State, StatesGroup
import scraper

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)


class FSMFillForm(StatesGroup):
    url_add = State()
    url_del = State()


@dp.message(Command('start'), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text='Привет! Я бот, который может отслеживать цены на товары из различных оналйн магазинов.\n\nДля того, чтобы'
             ' начать отслеживать цену на товар, выбери в меню команду "Добавить ссылку на товар".\nЕсли ты захочешь '
             'прекраить отслеживание, то выбери в меню пункт "Перестать отслеживать товар".\nЕсли окажется, что в нашей'
             ' базе нет сайта, цену с которого ты хочешь отслеживать - выбери команду "Обратная связь" и напиши '
             'название сайта. Также ты можешь написать любые свои пожелания, выбрав эту команду.'
             '\n\nПриятного использования :)'
    )


@dp.message(Command('addlink'))
async def process_addlink_command(message: Message,  state: FSMContext):
    await message.answer('Отправьте ссылку на товар: ')
    await state.set_state(FSMFillForm.url_add)


@dp.message(StateFilter(FSMFillForm.url_add))
async def process_del_command(message: Message, state: FSMContext):
    await state.update_data(url_add=message.text)
    result = await scraper.website_recognition(message.text)
    await message.answer(result)


if __name__ == '__main__':
    dp.run_polling(bot)
