import asyncio
import threading
from datetime import time

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from my_token import TOKEN
import price_check
from handlers import router

my_bot = Bot(token=TOKEN)


async def start_checking_price():
    while True:
        results = await price_check.check_and_update_prices()
        for user_id in results:
            try:
                await my_bot.send_message(user_id, results[user_id])
            except Exception as e:
                print(f"Не удалось отправить сообщение: {e}")
        await asyncio.sleep(600)


def run_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_checking_price())
    finally:
        loop.close()


thread = threading.Thread(target=run_event_loop)
thread.start()


async def main():
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    await dp.start_polling(my_bot),

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
