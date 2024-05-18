import asyncio
import threading
from datetime import datetime
<<<<<<< HEAD
from aiogram import Router
=======
from aiogram import Router, types, F, Bot
>>>>>>> e2a164cd7d6ea461f958ba77ba3bf8e9ab2b4dc0
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import manipulation_db
import price_check
import scraper

router = Router()


class Register(StatesGroup):
    url_add = State()
    feedback = State()


@router.message(CommandStart())
async def process_start_command(message: Message):

    user_id = message.from_user.id
    username = message.from_user.username
    if username is None:
        username = 'unknown'
    await manipulation_db.add_user_to_db(user_id, username)

    await message.answer(
        text='Привет! Я бот, который может отслеживать цены на товары из различных оналйн магазинов.\n\nДля того, чтобы'
             ' начать отслеживать цену на товар, выбери в меню команду "Добавить ссылку на товар".\nЕсли ты захочешь '
             'прекраить отслеживание, то выбери в меню пункт "Перестать отслеживать товар".\nЕсли окажется, что в нашей'
             ' базе нет сайта, цену с которого ты хочешь отслеживать - выбери команду "Обратная связь" и напиши '
             'название сайта. Также ты можешь написать любые свои пожелания, выбрав эту команду.'
             '\n\nПриятного использования :)'
    )


@router.message(Command('addlink'))
async def process_addlink_command(message: Message,  state: FSMContext):
    user_id = message.from_user.id
    current_products = await manipulation_db.tracking_products(user_id)
    if len(current_products) >= 5:
        await message.answer("Вы уже добавили максимально допустимое количество товаров (5).")
        await state.set_state(None)
    else:
<<<<<<< HEAD
        await message.answer('Отправьте ссылку на товар: ')
        await state.set_state(Register.url_add)


@router.message(Register.url_add)
async def process_add_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(url_add=message.text)
    await message.answer('Это может занять некоторое время🥺')
    try:
        message_text = await asyncio.wait_for(scraper.website_recognition(message.text, user_id), 30)
    except asyncio.TimeoutError:
        message_text = 'Извините, что-то пошло не так, попробуйте еще раз отправить ссылку.'
=======
        await state.update_data(url_add=message.text)
        await message.answer('Это может занять некоторое время🥺')
        message_text = ''
        try:
            message_text = await asyncio.wait_for(scraper.website_recognition(message.text, user_id), 30)
        except asyncio.TimeoutError:
            message_text = 'Извините, что-то пошло не так, попробуйте еще раз отправить ссылку.'
            await message.answer(message_text)
            await state.set_state(Register.url_add)
>>>>>>> e2a164cd7d6ea461f958ba77ba3bf8e9ab2b4dc0
        await message.answer(message_text)
        await state.set_state(Register.url_add)
    await message.answer(message_text)
    await state.set_state(None)


@router.message(Command('remove'))
async def process_dellink_command(message: Message):
    user_id = message.from_user.id
    products = await manipulation_db.tracking_products(user_id)
    tracking_buttons = []
    for idx, product in enumerate(products):
        button = InlineKeyboardButton(text=str(product), callback_data=str(idx))
        tracking_buttons.append([button])

    keyboard = InlineKeyboardMarkup(inline_keyboard=tracking_buttons)
    await message.answer("Выберите товар, за ценой которого больше не хотите следить:", reply_markup=keyboard)


@router.callback_query()
async def callback_query_handler(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    for row in callback_query.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data == callback_query.data:
                deleted_product = button.text
                break
    await manipulation_db.remove_products(user_id, deleted_product)
    await callback_query.message.answer(f'Товар {deleted_product} больше не отслеживается.')


@router.message(Command('feedback'))
async def process_feedback_command(message: Message,  state: FSMContext):
    await message.answer('Можете написать что угодно :) ')
    await state.set_state(Register.feedback)


@router.message(Register.feedback)
async def process_feedback_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    await state.update_data(feedback=message.text)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file = open('feedback.txt', 'a+')
    file.write(f'{now}: {user_id}, {username}: {message.text}\n')
    file.close()
    await message.answer('Спасибо за обратную связь!')
    await state.set_state(None)
