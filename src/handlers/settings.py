import html
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from src.user_manager import user_manager
from src.states import AddKeyword, AddCity, SetPrice, SetInterval
from src.keyboards.keyboard import (
    browser_keyboard,
    remove_keyword_keyboard,
    remove_city_keyboard,
)
from src.parsing import normalize_city_name

router = Router()

# ==================== /settings ====================
@router.message(Command("settings"))
async def cmd_settings(message: types.Message):
    user_id = message.from_user.id
    settings = user_manager.get_settings(user_id)

    # Keywords
    keywords = "\n".join(f"• {kw}" for kw in settings.keywords)

    # Cities
    cities_list = []
    for city in settings.cities:
        if city == "all":
            cities_list.append("• Все города (Avito)")
        else:
            cities_list.append(f"• {city}")
    cities = "\n".join(cities_list)

    interval_hours = settings.interval // 3600
    browser = settings.browser.capitalize()
    category_display = "все категории" if settings.avito_category == "all" else settings.avito_category

    status_msg = (
        "⚙️ <b>Текущие настройки мониторинга:</b>\n\n"
        f"🔑 <b>Ключевые слова:</b>\n{keywords}\n\n"
        f"🏙️ <b>Города поиска:</b>\n{cities}\n\n"
        f"📂 <b>Категория Avito:</b> {category_display}\n"
        f"💵 <b>Максимальная цена:</b> {settings.max_price} руб\n"
        f"⏱ <b>Интервал проверки:</b> {interval_hours} ч\n"
        f"🖥️ <b>Браузер:</b> {browser}\n\n"
        f"🟢 <b>Статус мониторинга:</b> {'Запущен' if user_manager.is_monitoring(user_id) else 'Остановлен'}"
    )

    await message.answer(status_msg, parse_mode="HTML")


# ==================== Ключевые слова ====================
@router.message(Command("keywords"))
async def show_keywords(message: types.Message):
    user_id = message.from_user.id
    settings = user_manager.get_settings(user_id)
    keywords = "\n".join(f"• {kw}" for kw in settings.keywords)
    await message.answer(f"🔑 <b>Текущие ключевые слова:</b>\n{keywords}", parse_mode="HTML")


@router.message(Command("add_keyword"))
async def add_keyword_start(message: types.Message, state: FSMContext):
    await message.answer("📝 Введите новое ключевое слово для поиска:")
    await state.set_state(AddKeyword.waiting_for_keyword)


@router.message(AddKeyword.waiting_for_keyword)
async def add_keyword_finish(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    keyword = message.text.strip()
    if not keyword:
        await message.answer("❌ Ключевое слово не может быть пустым")
        return
    settings = user_manager.get_settings(user_id)
    if keyword in settings.keywords:
        await message.answer("⚠️ Это ключевое слово уже есть в списке")
        await state.clear()
        return
    settings.keywords.append(keyword)
    await message.answer(f"✅ Добавлено ключевое слово: <b>{html.escape(keyword)}</b>", parse_mode="HTML")
    await state.clear()


@router.message(Command("remove_keyword"))
async def remove_keyword_start(message: types.Message):
    user_id = message.from_user.id
    settings = user_manager.get_settings(user_id)
    if not settings.keywords:
        await message.answer("ℹ️ Список ключевых слов пуст")
        return
    await message.answer(
        "🗑️ Выберите ключевое слово для удаления:",
        reply_markup=remove_keyword_keyboard(settings.keywords)
    )


@router.callback_query(F.data.startswith("remove_kw_"))
async def remove_keyword_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    index = int(callback.data.split("_")[-1])
    settings = user_manager.get_settings(user_id)
    if 0 <= index < len(settings.keywords):
        removed = settings.keywords.pop(index)
        await callback.message.edit_text(
            f"✅ Удалено ключевое слово: <b>{html.escape(removed)}</b>",
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ Ошибка удаления")
    await callback.answer()


# ==================== Города ====================
@router.message(Command("cities"))
async def show_cities(message: types.Message):
    user_id = message.from_user.id
    settings = user_manager.get_settings(user_id)
    cities_list = []
    for city in settings.cities:
        if city == "all":
            cities_list.append("• Все города (Avito)")
        else:
            cities_list.append(f"• {city}")
    cities = "\n".join(cities_list)
    await message.answer(
        f"🏙️ <b>Текущие города для поиска:</b>\n{cities}\n\n"
        f"<i>Примечание: 'Все города' работает только для Avito</i>",
        parse_mode="HTML"
    )


@router.message(Command("add_city"))
async def add_city_start(message: types.Message, state: FSMContext):
    await message.answer(
        "🌆 Введите название города для добавления:\n"
        "<i>Пример: Москва, Санкт-Петербург, Казань</i>\n"
        "Для поиска по всем городам введите: <b>все</b>",
        parse_mode="HTML"
    )
    await state.set_state(AddCity.waiting_for_city)


@router.message(AddCity.waiting_for_city)
async def add_city_finish(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    city_input = message.text.strip()
    if not city_input:
        await message.answer("❌ Название города не может быть пустым")
        return
    city = normalize_city_name(city_input)
    settings = user_manager.get_settings(user_id)
    if city in settings.cities:
        display = "Все города (Avito)" if city == "all" else city
        await message.answer(f"⚠️ <b>{html.escape(display)}</b> уже есть в списке", parse_mode="HTML")
        await state.clear()
        return
    settings.cities.append(city)
    display = "Все города (Avito)" if city == "all" else city
    await message.answer(f"✅ Добавлен: <b>{html.escape(display)}</b>", parse_mode="HTML")
    await state.clear()


@router.message(Command("remove_city"))
async def remove_city_start(message: types.Message):
    user_id = message.from_user.id
    settings = user_manager.get_settings(user_id)
    if not settings.cities:
        await message.answer("ℹ️ Список городов пуст")
        return
    await message.answer(
        "🗑️ Выберите город для удаления:",
        reply_markup=remove_city_keyboard(settings.cities)
    )


@router.callback_query(F.data.startswith("remove_city_"))
async def remove_city_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    index = int(callback.data.split("_")[-1])
    settings = user_manager.get_settings(user_id)
    if 0 <= index < len(settings.cities):
        removed = settings.cities.pop(index)
        display = "Все города (Avito)" if removed == "all" else removed
        await callback.message.edit_text(
            f"✅ Удален: <b>{html.escape(display)}</b>",
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ Ошибка удаления")
    await callback.answer()


# ==================== Максимальная цена ====================
@router.message(Command("price"))
async def set_price_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    current = user_manager.get_settings(user_id).max_price
    await message.answer(
        f"💵 Текущая максимальная цена: <b>{current} руб</b>\n"
        "Введите новое значение (только цифры, 0 - без ограничения):",
        parse_mode="HTML"
    )
    await state.set_state(SetPrice.waiting_for_price)


@router.message(SetPrice.waiting_for_price)
async def set_price_finish(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        price = int(message.text)
        if price < 0:
            raise ValueError
        user_manager.get_settings(user_id).max_price = price
        await message.answer(f"✅ Максимальная цена установлена: <b>{price} руб</b>", parse_mode="HTML")
    except ValueError:
        await message.answer("❌ Неверный формат цены. Введите целое число ≥ 0")
    finally:
        await state.clear()


# ==================== Интервал проверки ====================
@router.message(Command("interval"))
async def set_interval_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    current_hours = user_manager.get_settings(user_id).interval // 3600
    await message.answer(
        f"⏱ Текущий интервал проверки: <b>{current_hours} ч</b>\n"
        "Введите новый интервал в часах (1-24):",
        parse_mode="HTML"
    )
    await state.set_state(SetInterval.waiting_for_interval)


@router.message(SetInterval.waiting_for_interval)
async def set_interval_finish(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        hours = int(message.text)
        if hours < 1 or hours > 24:
            raise ValueError
        user_manager.get_settings(user_id).interval = hours * 3600
        await message.answer(f"✅ Интервал проверки установлен: <b>{hours} ч</b>", parse_mode="HTML")
    except ValueError:
        await message.answer("❌ Неверный формат. Введите число от 1 до 24")
    finally:
        await state.clear()


# ==================== Выбор браузера ====================
@router.message(Command("browser"))
async def set_browser(message: types.Message):
    user_id = message.from_user.id
    settings = user_manager.get_settings(user_id)
    await message.answer(
        f"🖥️ Текущий браузер: <b>{settings.browser.capitalize()}</b>\nВыберите браузер:",
        reply_markup=browser_keyboard(settings.browser)
    )


@router.callback_query(F.data.startswith("browser_"))
async def process_browser(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    browser = callback.data.split("_")[1]
    user_manager.get_settings(user_id).browser = browser
    await callback.message.edit_text(
        f"✅ Браузер изменен на: <b>{browser.capitalize()}</b>",
        parse_mode="HTML"
    )
    await callback.answer()
