import logging
import asyncio
from src.create_bot import dp, bot
from src.handlers import start, settings, monitor, category

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("monitor.log"), logging.StreamHandler()]
)

def start_bot():
    # Include routers
    dp.include_router(start.router)
    dp.include_router(settings.router)
    dp.include_router(monitor.router)
    dp.include_router(category.router)

    async def on_startup():
        logging.info("Bot started")

    async def on_shutdown():
        logging.info("Bot shutting down")
        # Stop all monitoring tasks
        from src.user_manager import user_manager
        for user_id in list(user_manager.monitoring_tasks.keys()):
            await user_manager.stop_monitoring(user_id)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        asyncio.run(dp.start_polling(bot))
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
