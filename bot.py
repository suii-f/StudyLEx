import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from deep_translator import GoogleTranslator



TOKEN = "token" 




logging.basicConfig(level=logging.INFO)


bot = Bot(token=TOKEN)
dp = Dispatcher()


user_dictionary = {} 

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


@dp.message(Command("train"))
async def cmd_train(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_dictionary or not user_dictionary[user_id]:
        await message.answer("Ваш словарь пуст! Сначала переведите пару слов и нажмите 'Сохранить'.")
        return

    
    word, translation = list(user_dictionary[user_id].items())[0]
    
  
    builder = InlineKeyboardBuilder()
    builder.button(text="Показать перевод", callback_data=f"show_{translation}")
    
    await message.answer(f"🧐 Как переводится: **{word}**?", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("show_"))
async def show_translation(callback: types.CallbackQuery):
    translation = callback.data.split("_")[1]
    await callback.message.edit_text(f"Правильный ответ: **{translation}** ✅")


@dp.callback_query(F.data.startswith("save_"))
async def save_word(callback: types.CallbackQuery):
   
    _, original, translated = callback.data.split("_", 2)
    user_id = callback.from_user.id
    
    if user_id not in user_dictionary:
        user_dictionary[user_id] = {}
    
    
    user_dictionary[user_id][original] = translated
    
    await callback.answer("Слово сохранено! 🎉") 
    await callback.message.edit_text(f"✅ Слово **{original}** добавлено в словарь.\nНажми /train чтобы учить.")


@dp.message()
async def translate_message(message: types.Message):
    text = message.text
    
    
    if any("\u0400" <= char <= "\u04FF" for char in text):
        src_lang = 'ru'
        target_lang = 'en'
    else:
        src_lang = 'en'
        target_lang = 'ru'

    try:
       
        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        
        
        builder = InlineKeyboardBuilder()
        
        if len(text) < 20 and len(translated_text) < 20:
            builder.button(text="➕ Сохранить в словарь", callback_data=f"save_{text}_{translated_text}")
        
        await message.answer(
            f"🇺🇸/🇷🇺 Перевод:\n\n**{translated_text}**", 
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        await message.answer("Не удалось перевести. Попробуйте другое слово.")


async def main():
   
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
