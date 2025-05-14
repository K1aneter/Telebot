import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.methods import DeleteWebhook
from aiogram.types import Message
import requests
from collections import defaultdict



# Токен вашего бота
TOKEN = '8138336556:AAHwfihp6Er6q_TlQwEB4UHTKwIajqO_X7w'

logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher()

# Бот сохраняет последние 3 сообщение
user_message_history = defaultdict(list)
MAX_HISTORY = 3

# Обработка команды start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id

    user_message_history[user_id] = []
    await message.answer('🤗Это бот, задавай любой вопрос, могу!', parse_mode='HTML')


@dp.message()
async def filter_messages(message: Message):
    user_id = message.from_user.id
    await message.answer("🤔 <i>Обрабатываю ваш вопрос...</i>", parse_mode="HTML")

    user_message_history[user_id].append({
        "role": "user",
        "content": message.text
    })

    if len(user_message_history[user_id]) > MAX_HISTORY:
        user_message_history[user_id] = user_message_history[user_id][-MAX_HISTORY:]

    url = "https://api.intelligence.io.solutions/api/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6ImVhZDg1OTE2LTY0MjctNGQwNi05ZmFjLWNjNWZkZDUyZDk3NSIsImV4cCI6NDg5OTg4NTQ1Nn0.caw1eso5nVNcJd0kT9EehuPDvtr9rahM--mO_uxQtdGcF5ou72GqVjjrdXlxnYBqVqj__awCaz8lB5vBiRcBbg",
    }

    # Формируем сообщения для API
    messages = [{"role": "system", "content": "You are a useful assistant who writes using emoticons."}]
    messages.extend(user_message_history[user_id])

    data = {
        "model": "deepseek-ai/DeepSeek-R1",
        "messages": messages,
    }

    response = requests.post(url, headers=headers, json=data)
    data = response.json()

    text = data['choices'][0]['message']['content']
    bot_text = text.split('</think>\n\n')[1]

    user_message_history[user_id].append({
        "role": "assistant",
        "content": bot_text
    })

    if len(user_message_history[user_id]) > MAX_HISTORY:
        user_message_history[user_id] = user_message_history[user_id][-MAX_HISTORY:]

    await message.answer(bot_text, parse_mode="Markdown")


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == "__main__":
    from aiogram.enums import ParseMode
    dp.run_polling(bot, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
