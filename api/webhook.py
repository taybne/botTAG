import os

from fastapi import FastAPI, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from handlers import router

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    if WEBHOOK_URL:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(WEBHOOK_URL)

@app.post("/api/webhook")
async def telegram_webhook(request: Request) -> Response:
    update = await request.json()
    await dp.feed_webhook_update(bot=bot, update=update)
    return Response(status_code=200)
