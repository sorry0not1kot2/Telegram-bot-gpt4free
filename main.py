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

# Словарь для хранения истории разговоров
conversation_history = {}

# Функция для обрезки истории разговора
def trim_history(history, max_length=4096):
    current_length = sum(len(message["content"]) for message in history)
    while history and current_length > max_length:
        removed_message = history.pop(0)
        current_length -= len(removed_message["content"])
    return history

async def get_gpt_response(chat_history):
    try:
        response = await g4f.ChatCompletion.create_async(
            model="gpt-3.5-turbo",  # Используйте правильное имя модели
            messages=chat_history,
            provider=g4f.Provider.You  # Используйте указанного провайдера
        )
        response_text = response.choices[0].message.content or ""
        logger.info(f"Ответ от GPT: {response_text}")
        return response_text
    except Exception as e:
        logger.error(f"Ошибка при получении ответа от GPT: {str(e)}")
        return f"Произошла ошибка при обращении к GPT: {str(e)}"

def split_message(message, max_length=4096):
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]

@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_input = message.text

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # Добавляем сообщения от пользователя в историю
    conversation_history[user_id].append({"role": "user", "content": user_input})
    conversation_history[user_id] = trim_history(conversation_history[user_id])

    chat_history = conversation_history[user_id]

    if user_input:
        logger.info(f"Получен запрос: {user_input}")
        await message.answer("Обрабатываю ваш запрос...")
        
        response = await get_gpt_response(chat_history)
        
        # Проверка на наличие HTML-кода
        if re.search(r'<[^>]+>', response):
            logger.error(f"Получен HTML-код вместо текста: {response}")
            response = "Извините, произошла ошибка. Ответ содержит некорректные данные."

        # Разделение длинного сообщения на части
        messages = split_message(response)
        for msg in messages:
            await message.reply(msg)
        
        # Добавляем сообщения от GPT в историю
        conversation_history[user_id].append({"role": "assistant", "content": response})
        conversation_history[user_id] = trim_history(conversation_history[user_id])
        
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
