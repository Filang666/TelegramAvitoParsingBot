from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def browser_keyboard(current: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Firefox" + (" ✅" if current == "firefox" else ""), callback_data="browser_firefox"),
            InlineKeyboardButton(text="Chrome" + (" ✅" if current == "chrome" else ""), callback_data="browser_chrome")
        ]
    ])
    return kb

def remove_keyword_keyboard(keywords: list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"❌ {kw}", callback_data=f"remove_kw_{i}")]
        for i, kw in enumerate(keywords)
    ])
    return kb

def remove_city_keyboard(cities: list) -> InlineKeyboardMarkup:
    buttons = []
    for i, city in enumerate(cities):
        display = "Все города (Avito)" if city == "all" else city
        buttons.append([InlineKeyboardButton(text=f"❌ {display}", callback_data=f"remove_city_{i}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def category_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить категорию", callback_data="set_category")]
    ])
    return kb
