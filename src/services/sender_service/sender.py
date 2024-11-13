from aiogram import Bot


class SenderService:
    def __init__(self, bot: Bot):
        self.bot = bot

    def send_range(self, message: str, users_id: list[int]):
        for user_id in users_id:
            self.bot.send_message(user_id, message)

        
