import logging
import os
import requests
from aiogram import Bot, Dispatcher, types
import g4f
from aiogram.utils import executor
import re
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
API_TOKEN = os.getenv('API_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def get_gpt_response(query):
    try:
        response = await g4f.ChatCompletion.create_async(
            model="gpt-4",  # Используйте правильное имя модели
            messages=[{"role": "user", "content": query}],
        )
        return response
    except Exception as e:
        logger.error(f"Ошибка при получении ответа от GPT: {str(e)}")
        return f"Произошла ошибка при обращении к GPT: {str(e)}"

def split_message(message, max_length=4096):
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]

@dp.message_handler()
async def handle_message(message: types.Message):
    query = message.text
    
    if query:
        logger.info(f"Получен запрос: {query}")
        await message.answer("Обрабатываю ваш запрос...")
        
        response = await get_gpt_response(query)
        
        # Проверка на наличие HTML-кода
        if re.search(r'<[^>]+>', response):
            response = "Извините, произошла ошибка. Ответ содержит некорректные данные."

        # Разделение длинного сообщения на части
        messages = split_message(response)
        for msg in messages:
            await message.reply(msg)
        
        logger.info("Ответ отправлен")
    else:
        await message.reply("Пожалуйста, введите сообщение.")

# Функция для запуска бота
async def main():
    try:
        logger.info("Запуск бота...")
        await dp.start_polling()
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {str(e)}")

# Запуск бота
if __name__ == '__main__':
    asyncio.run(main())
