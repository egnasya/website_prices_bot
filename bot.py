import asyncio
<<<<<<< HEAD
from aiogram import Bot, Dispatcher

=======
import logging
import threading
from asyncio import get_event_loop
from aiogram import Bot, Dispatcher

from aiogram.client import bot
from aiogram.fsm.storage.memory import MemoryStorage

>>>>>>> e2a164cd7d6ea461f958ba77ba3bf8e9ab2b4dc0
import price_check
from my_token import TOKEN
from handlers import router


async def main():
    my_bot = Bot(token=TOKEN)
    dp = Dispatcher(bot=my_bot)
    dp.include_router(router)

    async def start_checking_price(wait_for: int):
        while True:
            results = await price_check.check_and_update_prices()
            for user_id, messages in results.items():
                for message in messages:
                    try:
                        await my_bot.send_message(user_id, message)
                    except Exception as e:
                        print(f"Не удалось отправить сообщение: {e}")
                print('-----------------------------------------------------------------------------------------------')
            await asyncio.sleep(wait_for)

<<<<<<< HEAD
    check_task = asyncio.create_task(start_checking_price(5400))
=======
    check_task = asyncio.create_task(start_checking_price(1800))
>>>>>>> e2a164cd7d6ea461f958ba77ba3bf8e9ab2b4dc0

    try:
        await dp.start_polling(my_bot)
    finally:
        check_task.cancel()
        try:
            await check_task
        except asyncio.CancelledError:
            pass
        await my_bot.close()


if __name__ == '__main__':
    asyncio.run(main())