from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from my_token import TOKEN


# создание объектов бота и диспечера
bot = Bot(token=TOKEN)
dp = Dispatcher()


# хендлер, который срабатывает на команду 'start'
@dp.message(Command(commands=['start']))
async def process_start_command(message: Message):
    await message.answer('Привет! Я бот, который может отслеживать цены на товары из различных оналйн магазинов.\n\n'
                         'Для того, чтобы начать отслеживать цену на товар, выбери в меню команду "Добавить ссылку на '
                         'товар" и отправь мне ссылку на этот товар.\nЕсли ты захочешь прекраить отслеживание, то '
                         'выбери в меню пункт "Перестать отслеживать товар" и выбери товар из списка.\n'
                         'Если окажется, что в нашей базе нет сайта, цену с которого ты хочешь отслеживать - выбери '
                         'команду "Обратная связь" и напиши название сайта.\n\nПриятного использования :)')

if __name__ == '__main__':
    dp.run_polling(bot)
