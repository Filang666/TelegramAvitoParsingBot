import asyncio
from typing import Dict, Optional
from dataclasses import dataclass, field
from src.parsing import monitor_user
from src.read import load_seen_ids

@dataclass
class UserSettings:
    keywords: list = field(default_factory=lambda: ["ноутбук", "видеокарта", "процессор"])
    cities: list = field(default_factory=lambda: ["moskva"])
    max_price: int = 25000
    interval: int = 3600
    browser: str = "firefox"
    avito_category: str = "all"

class UserManager:
    def __init__(self):
        self.settings: Dict[int, UserSettings] = {}
        self.monitoring_active: Dict[int, bool] = {}
        self.monitoring_tasks: Dict[int, asyncio.Task] = {}
        self.seen_ids = load_seen_ids()

    def get_settings(self, user_id: int) -> UserSettings:
        return self.settings.setdefault(user_id, UserSettings())

    async def start_monitoring(self, user_id: int):
        if self.monitoring_active.get(user_id):
            return
        self.monitoring_active[user_id] = True
        task = asyncio.create_task(monitor_user(user_id, self))
        self.monitoring_tasks[user_id] = task

    async def stop_monitoring(self, user_id: int):
        self.monitoring_active[user_id] = False
        task = self.monitoring_tasks.get(user_id)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self.monitoring_tasks[user_id]

    def is_monitoring(self, user_id: int) -> bool:
        return self.monitoring_active.get(user_id, False)

user_manager = UserManager()
