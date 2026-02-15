from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from src.user_manager import user_manager
from src.states import SetCategory
from src.parsing import normalize_category_name
import html

router = Router()

@router.message(Command("category"))
async def cmd_category(message: types.Message, state: FSMContext):
    await message.answer(
        "✏️ Введите категорию для поиска на Avito (или 'все' для всех категорий):\n"
        "<i>Пример: ноутбуки, телефоны, видеокарты</i>",
        parse_mode="HTML"
    )
    await state.set_state(SetCategory.waiting_for_category)

@router.message(SetCategory.waiting_for_category)
async def set_category_finish(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    category_input = message.text.strip()
    if not category_input:
        await message.answer("❌ Название категории не может быть пустым")
        return
    category = normalize_category_name(category_input)
    settings = user_manager.get_settings(user_id)
    settings.avito_category = category
    display = "все категории" if category == "all" else category
    await message.answer(
        f"✅ Категория Avito установлена: <b>{html.escape(display)}</b>",
        parse_mode="HTML"
    )
    await state.clear()
