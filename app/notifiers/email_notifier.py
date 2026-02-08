"""
Email notification sender using SMTP.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from .base_notifier import BaseNotifier
from .templates import format_text_report, format_html_report
from app.detection.base_detector import ChangeReport


class EmailNotifier(BaseNotifier):
    """
    Email notifier using SMTP with TLS.
    
    Sends HTML emails with change detection reports.
    """

    def __init__(
        self, 
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        to_email: str,
        from_email: Optional[str] = None
    ):
        """
        Initialize the email notifier.
        
        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port (usually 587 for TLS)
            username: SMTP login username
            password: SMTP login password
            to_email: Recipient email address
            from_email: Sender email (defaults to username)
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.to_email = to_email
        self.from_email = from_email or username

    def notify(self, change_report: ChangeReport, source_name: str = None) -> None:
        """
        Send email notification with change report.
        
        Args:
            change_report: The change report to send
            source_name: Optional source identifier for subject line
        """
        # Only send if there are changes
        if not change_report.has_changes:
            return
        
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = self._create_subject(change_report, source_name)
            msg["From"] = self.from_email
            msg["To"] = self.to_email

            # Plain text version
            text_body = format_text_report(change_report, source_name)
            msg.attach(MIMEText(text_body, "plain"))

            # HTML version
            html_body = format_html_report(change_report, source_name)
            msg.attach(MIMEText(html_body, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.from_email, self.to_email, msg.as_string())
            
            print(f"📧 Email sent to {self.to_email}")
            
        except smtplib.SMTPAuthenticationError:
            print("❌ Email failed: Authentication error. Check username/password.")
        except smtplib.SMTPException as e:
            print(f"❌ Email failed: {e}")
        except Exception as e:
            print(f"❌ Email failed: {e}")

    def _create_subject(self, report: ChangeReport, source_name: str = None) -> str:
        """Create email subject line."""
        source = source_name or "SWMAP"
        return f"🔔 [{source}] {report.summary()}"
