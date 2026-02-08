"""
Notification Manager - Multi-channel dispatcher.
Automatically configures notifiers based on environment settings.
"""
from typing import List

from .base_notifier import BaseNotifier
from .console_notifier import ConsoleNotifier
from .email_notifier import EmailNotifier
from .telegram_notifier import TelegramNotifier
from app.detection.base_detector import ChangeReport
from app.core.config import settings


class NotificationManager:
    """
    Manages multiple notification channels.
    
    Automatically configures enabled notifiers from settings and
    dispatches change reports to all of them.
    """

    def __init__(self, include_console: bool = True):
        """
        Initialize the notification manager.
        
        Args:
            include_console: Whether to include console output (default: True)
        """
        self.notifiers: List[BaseNotifier] = []
        
        # Always add console notifier if requested
        if include_console:
            self.notifiers.append(ConsoleNotifier(use_colors=True, verbose=True))
        
        # Add email notifier if enabled
        if settings.EMAIL_ENABLED:
            self._setup_email_notifier()
        
        # Add Telegram notifier if enabled
        if settings.TELEGRAM_ENABLED:
            self._setup_telegram_notifier()

    def _setup_email_notifier(self):
        """Configure email notifier from settings."""
        if not settings.EMAIL_USERNAME or not settings.EMAIL_PASSWORD:
            print("⚠️ Email enabled but credentials not set. Skipping email notifier.")
            return
        
        if not settings.EMAIL_TO:
            print("⚠️ Email enabled but recipient not set. Skipping email notifier.")
            return
        
        try:
            notifier = EmailNotifier(
                smtp_host=settings.EMAIL_SMTP_HOST,
                smtp_port=settings.EMAIL_SMTP_PORT,
                username=settings.EMAIL_USERNAME,
                password=settings.EMAIL_PASSWORD,
                to_email=settings.EMAIL_TO,
                from_email=settings.EMAIL_FROM or settings.EMAIL_USERNAME
            )
            self.notifiers.append(notifier)
            print("✅ Email notifications enabled")
        except Exception as e:
            print(f"⚠️ Failed to setup email notifier: {e}")

    def _setup_telegram_notifier(self):
        """Configure Telegram notifier from settings."""
        if not settings.TELEGRAM_BOT_TOKEN:
            print("⚠️ Telegram enabled but bot token not set. Skipping Telegram notifier.")
            return
        
        if not settings.TELEGRAM_CHAT_ID:
            print("⚠️ Telegram enabled but chat ID not set. Skipping Telegram notifier.")
            return
        
        try:
            notifier = TelegramNotifier(
                bot_token=settings.TELEGRAM_BOT_TOKEN,
                chat_id=settings.TELEGRAM_CHAT_ID
            )
            self.notifiers.append(notifier)
            print("✅ Telegram notifications enabled")
        except Exception as e:
            print(f"⚠️ Failed to setup Telegram notifier: {e}")

    def add_notifier(self, notifier: BaseNotifier) -> None:
        """
        Add a custom notifier to the manager.
        
        Args:
            notifier: A notifier instance implementing BaseNotifier
        """
        self.notifiers.append(notifier)

    def notify_all(self, change_report: ChangeReport, source_name: str = None) -> None:
        """
        Send notifications to all configured channels.
        
        Args:
            change_report: The change report to send
            source_name: Optional source identifier
        """
        for notifier in self.notifiers:
            try:
                notifier.notify(change_report, source_name)
            except Exception as e:
                notifier_name = notifier.__class__.__name__
                print(f"⚠️ {notifier_name} failed: {e}")

    @property
    def enabled_channels(self) -> List[str]:
        """Get list of enabled notification channel names."""
        return [n.__class__.__name__ for n in self.notifiers]
