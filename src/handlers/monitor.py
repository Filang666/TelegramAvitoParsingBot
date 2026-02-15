from aiogram import Router, types
from aiogram.filters import Command
from src.create_bot import bot
from src.user_manager import user_manager
from src.parsing import extract_price
import html
import logging
from typing import List, Dict

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("run"))
async def cmd_run(message: types.Message):
    user_id = message.from_user.id
    if user_manager.is_monitoring(user_id):
        await message.answer("ℹ️ Мониторинг уже запущен")
        return
    await user_manager.start_monitoring(user_id)
    settings = user_manager.get_settings(user_id)
    all_cities_note = "⚠️ <i>Поиск по 'всем городам' работает только для Avito</i>\n" if "all" in settings.cities else ""
    await message.answer(
        f"🚀 <b>Мониторинг Avito запущен!</b>\n"
        f"🖥️ <b>Браузер:</b> {settings.browser.capitalize()}\n"
        f"📂 <b>Категория:</b> {'все' if settings.avito_category == 'all' else settings.avito_category}\n"
        f"{all_cities_note}"
        f"⏱ <b>Следующая проверка через:</b> {settings.interval//60} мин",
        parse_mode="HTML"
    )

@router.message(Command("stop"))
async def cmd_stop(message: types.Message):
    user_id = message.from_user.id
    if not user_manager.is_monitoring(user_id):
        await message.answer("ℹ️ Мониторинг не был запущен")
        return
    await user_manager.stop_monitoring(user_id)
    await message.answer("🛑 <b>Мониторинг остановлен.</b> Чтобы снова запустить, используйте /run", parse_mode="HTML")

@router.message(Command("status"))
async def cmd_status(message: types.Message):
    user_id = message.from_user.id
    status = "🟢 <b>Мониторинг запущен</b>" if user_manager.is_monitoring(user_id) else "🔴 <b>Мониторинг остановлен</b>"
    await message.answer(status, parse_mode="HTML")

async def send_notification(user_id: int, ad: dict):
    """Send a single ad notification."""
    try:
        title = html.escape(ad['title'])
        price = html.escape(ad['price'])
        source = html.escape(ad['source'])
        city = html.escape(ad['city'])
        category = html.escape(ad.get('category', 'разное'))
        link = ad['link']
        text = (
            f"<b>🔥 НОВОЕ ОБЪЯВЛЕНИЕ!</b>\n"
            f"<b>Категория:</b> {category}\n"
            f"<b>Источник:</b> {source}, {city}\n\n"
            f"<b>{title}</b>\n"
            f"💵 <b>Цена:</b> {price}\n"
            f'🔗 <a href="{link}">Ссылка на объявление</a>'
        )
        await bot.send_message(user_id, text, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Failed to send notification to {user_id}: {e}")
        # fallback plain text
        try:
            await bot.send_message(
                user_id,
                f"Новое объявление! ({ad['source']}, {ad['city']})\n"
                f"Категория: {ad.get('category', 'разное')}\n\n"
                f"{ad['title']}\nЦена: {ad['price']}\nСсылка: {ad['link']}",
                disable_web_page_preview=True
            )
        except:
            pass

async def send_batch_summary(user_id: int, ads: List[Dict]):
    """Send a summary when more than 3 new ads are found."""
    count = len(ads)
    prices = []
    titles = []
    for ad in ads:
        price_val = extract_price(ad['price'])
        if price_val > 0:
            prices.append(price_val)
        titles.append(ad['title'])
    
    min_price = min(prices) if prices else "?"
    max_price = max(prices) if prices else "?"
    
    # Show first 3 titles as examples
    sample_titles = titles[:3]
    sample_text = "\n".join(f"• {html.escape(t)}" for t in sample_titles)
    if len(titles) > 3:
        sample_text += f"\n... и ещё {len(titles)-3}"
    
    text = (
        f"<b>🔥 Найдено новых объявлений: {count}</b>\n\n"
        f"<b>Примеры:</b>\n{sample_text}\n\n"
        f"<b>Диапазон цен:</b> {min_price} - {max_price} руб"
    )
    try:
        await bot.send_message(user_id, text, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Failed to send batch summary to {user_id}: {e}")
