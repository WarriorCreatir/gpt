import asyncio
import openai
import random
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import json

with open("config.json", "r") as f:
    config = json.load(f)

TELEGRAM_TOKEN = config["token"]
OPENAI_API_KEY = config["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY
bot = Bot(TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
question_button = KeyboardButton("Ask a question")
instagram_button = KeyboardButton("Instagram")
menu_keyboard.add(question_button, instagram_button)

# Задаем параметры для OpenAI
model_engine = "text-davinci-002"
max_tokens = 150
temperature = 0.5


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Hi! I'm a kid's bot. What would you like to do?", reply_markup=menu_keyboard
    )


@dp.message_handler(text="Ask a question")
async def ask_question(message: types.Message, state: FSMContext):
    await message.answer("What's your question?")
    await state.set_state("openai")


@dp.message_handler(state="openai")
async def process_question(message: types.Message, state: FSMContext):
    question = message.text
    # Получаем ответ от OpenAI
    prompt = f"Q: {question}\nA:"
    try:
        response = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        answer = response.choices[0].text.strip()
        await message.answer(answer)
    except Exception as e:
        print(f"Error: {e}")
        await message.answer("Sorry, there was an error. Please try again later.")
    finally:
        await state.finish()


@dp.message_handler(text="Instagram")
async def instagram(message: types.Message):
    instagram_url = "https://www.instagram.com/"
    await message.answer(f"Here's the link to our Instagram page: {instagram_url}")


@dp.message_handler()
async def unknown_command(message: types.Message):
    await message.answer(
        "I'm sorry, I didn't understand. Please choose one of the options from the menu."
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
