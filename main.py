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

@dp.message_handler(commands=['gpt'])
async def handle_gpt_command(message: types.Message):
    query = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else ''
    
    if query:
        logger.info(f"Получен запрос: {query}")
        await message.answer("Обрабатываю ваш запрос...")
        
        response = await get_gpt_response(query)
        
        await message.reply(response)
        logger.info("Ответ отправлен")
    else:
        await message.reply("Пожалуйста, введите запрос после команды /gpt")

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
