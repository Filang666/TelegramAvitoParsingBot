from aiogram import Router, types
from aiogram.filters import Command
from src.user_manager import user_manager

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_manager.get_settings(user_id)  # ensure defaults
    await message.answer(
        "🔎 <b>Универсальный монитор объявлений Avito активирован!</b>\n"
        "Настройте параметры поиска перед запуском:\n"
        "1. Ключевые слова (/keywords)\n"
        "2. Города (/cities)\n"
        "3. Категория Avito (/category)\n"
        "4. Макс. цену (/price)\n"
        "5. Интервал (/interval)\n"
        "6. Браузер (/browser)\n\n"
        "Когда всё настроите, запустите мониторинг командой /run\n\n"
        "<b>Основные команды:</b>\n"
        "/settings - текущие настройки\n"
        "/help - справка по всем командам",
        parse_mode="HTML"
    )

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "<b>📚 Справка по командам:</b>\n\n"
        "/start – начать\n/settings – настройки\n/keywords – управление ключевыми словами\n"
        "/add_keyword – добавить ключевое слово\n/remove_keyword – удалить\n"
        "/cities – управление городами\n/add_city – добавить город\n/remove_city – удалить\n"
        "/category – установить категорию Avito\n/price – макс. цена\n/interval – интервал\n"
        "/browser – выбор браузера\n/run – запуск\n/stop – остановка\n/status – статус\n/help – справка",
        parse_mode="HTML"
    )
