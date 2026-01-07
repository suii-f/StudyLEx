import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from deep_translator import GoogleTranslator

# ==========================================
# ВСТАВЬ СЮДА СВОЙ ТОКЕН ОТ BOTFATHER
TOKEN = "8581181236:AAEpwkd8PkhTBA1LuESmABso-YjH8J20LyE" 
# Пример: TOKEN = "603123123:AAFgdfsgsdfg..."
# ==========================================

# Включаем логирование, чтобы видеть ошибки в терминале
logging.basicConfig(level=logging.INFO)

# Создаем объекты бота
bot = Bot(token=TOKEN)
dp = Dispatcher()

# База данных в памяти (пока бот работает). 
# Для серьезного проекта нужна SQLite, но для теста хватит этого.
user_dictionary = {} 

# --- Хэндлер на команду /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! 👋\n"
        "Я бот-переводчик с функцией обучения.\n\n"
        "📖 **Как пользоваться:**\n"
        "Просто напиши мне любое слово или фразу.\n"
        "— Если на русском -> переведу на английский.\n"
        "— Если на английском -> переведу на русский.\n\n"
        "Попробуй прямо сейчас!"
    )

# --- Хэндлер на команду /train (Тренировка) ---
@dp.message(Command("train"))
async def cmd_train(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_dictionary or not user_dictionary[user_id]:
        await message.answer("Ваш словарь пуст! Сначала переведите пару слов и нажмите 'Сохранить'.")
        return

    # Берем первое попавшееся слово (для примера)
    word, translation = list(user_dictionary[user_id].items())[0]
    
    # Кнопка для проверки
    builder = InlineKeyboardBuilder()
    builder.button(text="Показать перевод", callback_data=f"show_{translation}")
    
    await message.answer(f"🧐 Как переводится: **{word}**?", reply_markup=builder.as_markup())

# --- Обработка нажатия кнопки "Показать перевод" ---
@dp.callback_query(F.data.startswith("show_"))
async def show_translation(callback: types.CallbackQuery):
    translation = callback.data.split("_")[1]
    await callback.message.edit_text(f"Правильный ответ: **{translation}** ✅")

# --- Обработка нажатия кнопки "Сохранить" ---
@dp.callback_query(F.data.startswith("save_"))
async def save_word(callback: types.CallbackQuery):
    # Формат данных в кнопке: save_СЛОВО_ПЕРЕВОД
    _, original, translated = callback.data.split("_", 2)
    user_id = callback.from_user.id
    
    if user_id not in user_dictionary:
        user_dictionary[user_id] = {}
    
    # Сохраняем в память
    user_dictionary[user_id][original] = translated
    
    await callback.answer("Слово сохранено! 🎉") # Всплывающее уведомление
    await callback.message.edit_text(f"✅ Слово **{original}** добавлено в словарь.\nНажми /train чтобы учить.")

# --- УМНЫЙ ПЕРЕВОДЧИК (Самая главная часть) ---
@dp.message()
async def translate_message(message: types.Message):
    text = message.text
    
    # Автоматическое определение: если есть русские буквы, переводим на англ, иначе наоборот
    if any("\u0400" <= char <= "\u04FF" for char in text):
        src_lang = 'ru'
        target_lang = 'en'
    else:
        src_lang = 'en'
        target_lang = 'ru'

    try:
        # Сам процесс перевода
        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        
        # Создаем кнопку "Сохранить в словарь"
        builder = InlineKeyboardBuilder()
        # В callback_data есть ограничение по длине, поэтому сохраняем только короткие слова
        if len(text) < 20 and len(translated_text) < 20:
            builder.button(text="➕ Сохранить в словарь", callback_data=f"save_{text}_{translated_text}")
        
        await message.answer(
            f"🇺🇸/🇷🇺 Перевод:\n\n**{translated_text}**", 
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        await message.answer("Не удалось перевести. Попробуйте другое слово.")

# --- ЗАПУСК БОТА ---
async def main():
    # Удаляем старые обновления, чтобы бот не отвечал на сообщения, присланные пока он спал
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
