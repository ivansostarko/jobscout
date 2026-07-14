"""Email delivery via SMTP (settings in .env)."""
from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..config import env

log = logging.getLogger("jobscout.email")


def send(subject: str, plain: str, html: str) -> bool:
    host = env("SMTP_HOST")
    port = int(env("SMTP_PORT", "587"))
    user = env("SMTP_USER")
    password = env("SMTP_PASSWORD")
    sender = env("EMAIL_FROM", user)
    to = [a.strip() for a in env("EMAIL_TO", user).split(",") if a.strip()]
    if not host or not user or not to:
        log.error("SMTP settings missing in .env (SMTP_HOST/SMTP_USER/EMAIL_TO)")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, sender, ", ".join(to)
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=30)
        else:
            server = smtplib.SMTP(host, port, timeout=30)
            server.starttls()
        with server:
            server.login(user, password)
            server.sendmail(sender, to, msg.as_string())
        log.info("Email report delivered to %s", to)
        return True
    except Exception as e:  # noqa: BLE001
        log.error("Email send failed: %s", e)
        return False
