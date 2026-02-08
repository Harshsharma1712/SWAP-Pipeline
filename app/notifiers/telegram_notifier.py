"""
Telegram notification sender using python-telegram-bot.
"""
import asyncio
from telegram import Bot
from telegram.error import TelegramError

from .base_notifier import BaseNotifier
from .templates import format_telegram_report
from app.detection.base_detector import ChangeReport


class TelegramNotifier(BaseNotifier):
    """
    Telegram notifier using python-telegram-bot.
    
    Sends formatted messages to a Telegram chat/channel.
    """

    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize the Telegram notifier.
        
        Args:
            bot_token: Bot token from @BotFather
            chat_id: Target chat/channel ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = Bot(token=bot_token)

    def notify(self, change_report: ChangeReport, source_name: str = None) -> None:
        """
        Send Telegram notification with change report.
        
        Args:
            change_report: The change report to send
            source_name: Optional source identifier
        """
        # Only send if there are changes
        if not change_report.has_changes:
            return
        
        try:
            message = format_telegram_report(change_report, source_name)
            
            # Run async send in sync context
            asyncio.run(self._send_message(message))
            
            print(f"📱 Telegram message sent to chat {self.chat_id}")
            
        except TelegramError as e:
            print(f"❌ Telegram failed: {e}")
        except Exception as e:
            print(f"❌ Telegram failed: {e}")

    async def _send_message(self, message: str) -> None:
        """Async method to send the Telegram message."""
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=message,
            parse_mode="MarkdownV2"
        )
