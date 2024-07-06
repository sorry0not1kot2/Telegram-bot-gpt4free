# файл main.py :
import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import g4f
import nest_asyncio

nest_asyncio.apply()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка бота
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN provided")
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

# Переменные для провайдера и модели
PROVIDER = g4f.Provider.DeepAI  # Замените на нужный провайдер
MODEL = g4f.models.gpt_4  # Или g4f.models.claude

# Словарь для хранения истории разговоров
conversation_history = {}

# Функция для обрезки истории разговора
def trim_history(history, max_length=4096):
    current_length = sum(len(message["content"]) for message in history)
    while history and current_length > max_length:
        removed_message = history.pop(0)
        current_length -= len(removed_message["content"])
    return history

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот, использующий GPT-4. Отправьте мне сообщение, и я постараюсь ответить.")

@dp.message_handler(commands=['clear'])
async def process_clear_command(message: types.Message):
    user_id = message.from_user.id
    conversation_history[user_id] = []
    await message.reply("История диалога очищена.")

# Обработчик для каждого нового сообщения
@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_input = message.text

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({"role": "user", "content": user_input})
    conversation_history[user_id] = trim_history(conversation_history[user_id])

    chat_history = conversation_history[user_id]

    try:
        response = await g4f.ChatCompletion.create_async(
            model=MODEL,
            messages=chat_history,
            provider=PROVIDER,
        )
        chat_gpt_response = response.choices[0].message.content 
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        chat_gpt_response = "Извините, произошла ошибка."

    conversation_history[user_id].append({"role": "assistant", "content": chat_gpt_response})
    logger.info(f"Conversation history: {conversation_history}")
    length = sum(len(message["content"]) for message in conversation_history[user_id])
    logger.info(f"Conversation length: {length}")
    await message.answer(chat_gpt_response)

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

