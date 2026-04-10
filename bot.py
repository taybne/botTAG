import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv
from handlers import router

# ===== Загрузка переменных из .env =====
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID") or 0)

if not BOT_TOKEN:
    print("⚠️ BOT_TOKEN not set, using dummy")
    BOT_TOKEN = "dummy_token"
if not ADMIN_ID:
    print("⚠️ ADMIN_ID not set, using dummy")
    ADMIN_ID = 0

# ===== Команды бота =====
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start TAG"),
        BotCommand(command="add", description="Add location"),
        BotCommand(command="feedback", description="Send feedback"),
    ]
    await bot.set_my_commands(commands)

async def main():
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(main())

if __name__ == "__main__":
    asyncio.run(main())
