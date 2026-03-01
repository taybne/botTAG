from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import (
    Message, ReplyKeyboardMarkup,
    KeyboardButton, InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from states import AddLocation, Feedback
import os

from dotenv import load_dotenv  
load_dotenv()
router = Router()

ADMIN_ID = int(os.getenv("ADMIN_ID") or 0)

# ===== MAIN MENU =====
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Add location")],
        [KeyboardButton(text="💬 Feedback")]
    ],
    resize_keyboard=True
)

# ===== FINISH BUTTON =====
finish_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Finish")]
    ],
    resize_keyboard=True
)

from aiogram.types import InputFile

# ===== START =====
@router.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "Welcome to TAG 🌍\nSend locations or feedback.",
        reply_markup=menu
    )
# ===== ADD LOCATION =====
@router.message(F.text == "📍 Add location")
async def add_location_start(message: Message, state: FSMContext):
    await state.set_state(AddLocation.name)
    await message.answer("Enter location name:")

@router.message(AddLocation.name)
async def location_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddLocation.description)
    await message.answer("Description (optional). Send '-' to skip.")

@router.message(AddLocation.description)
async def location_description(message: Message, state: FSMContext):
    desc = message.text if message.text != "-" else "—"
    await state.update_data(description=desc)
    await state.set_state(AddLocation.city)
    await message.answer("City:")

@router.message(AddLocation.city)
async def location_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(AddLocation.country)
    await message.answer("Country:")

@router.message(AddLocation.country)
async def location_country(message: Message, state: FSMContext):
    await state.update_data(country=message.text)
    await state.set_state(AddLocation.photos)
    await state.update_data(photos=[])

    await message.answer(
        "Send photos (at least 1).\nPress ✅ Finish when done.",
        reply_markup=finish_keyboard
    )

# ===== COLLECT PHOTOS (ПЕРВЫМ!) =====
@router.message(StateFilter(AddLocation.photos), F.photo)
async def collect_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer("Photo added ✅")

# ===== FINISH LOCATION (ВТОРЫМ! ПЕРЕД FALLBACK) =====
@router.message(StateFilter(AddLocation.photos), F.text == "✅ Finish")
async def finish_location(message: Message, state: FSMContext):
    print(f"DEBUG: Finish clicked! ADMIN_ID={ADMIN_ID}, state={await state.get_state()}")
    
    if ADMIN_ID == 0:
        await message.answer("❌ ADMIN_ID not set in .env!")
        return
        
    data = await state.get_data()

    if not data.get("photos"):
        await message.answer("You must send at least 1 photo.")
        return

    bot = message.bot
    text = (
        f"📍 NEW LOCATION\n\n"
        f"Name: {data['name']}\n"
        f"Description: {data['description']}\n"
        f"City: {data['city']}\n"
        f"Country: {data['country']}"
    )

    # отправка админу
    await bot.send_message(ADMIN_ID, text)
    for photo in data["photos"]:
        await bot.send_photo(ADMIN_ID, photo)

    await message.answer(
        "Thanks! ❤️ Location sent for moderation ✅",
        reply_markup=menu
    )
    await state.clear()
    print("DEBUG: Location sent and state cleared!")

# ===== FALLBACK (ПОСЛЕДНИМ!) =====
@router.message(StateFilter(AddLocation.photos))
async def photos_fallback(message: Message):
    await message.answer("Send a photo or press ✅ Finish.")

# ===== FEEDBACK =====
feedback_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⭐️ Review", callback_data="review")],
        [InlineKeyboardButton(text="⚠️ Problem", callback_data="problem")]
    ]
)

@router.message(F.text == "💬 Feedback")
async def feedback_menu(message: Message):
    await message.answer("Choose type:", reply_markup=feedback_keyboard)

@router.callback_query(F.data == "review")
async def review_start(callback, state: FSMContext):
    await state.set_state(Feedback.review)
    await callback.message.answer("Write your review:")
    await callback.answer()

@router.callback_query(F.data == "problem")
async def problem_start(callback, state: FSMContext):
    await state.set_state(Feedback.problem)
    await callback.message.answer("Describe the problem:")
    await callback.answer()

@router.message(Feedback.review)
async def send_review(message: Message, state: FSMContext):
    bot = message.bot
    if ADMIN_ID == 0:
        await message.answer("❌ ADMIN_ID not set!")
        return
    await bot.send_message(
        ADMIN_ID,
        f"⭐️ REVIEW\n\nFrom @{message.from_user.username}\n{message.text}"
    )
    await message.answer("Thanks for feedback ❤️")
    await state.clear()

@router.message(Feedback.problem)
async def send_problem(message: Message, state: FSMContext):
    bot = message.bot
    if ADMIN_ID == 0:
        await message.answer("❌ ADMIN_ID not set!")
        return
    await bot.send_message(
        ADMIN_ID,
        f"⚠️ PROBLEM\n\nFrom @{message.from_user.username}\n{message.text}"
    )
    await message.answer("Problem reported ✅")
    await state.clear()
