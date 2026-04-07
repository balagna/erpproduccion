import smtplib
from email.mime.text import MIMEText
from flask import current_app

def send_email(subject, recipient, body):
    if not current_app.config["MAIL_ENABLED"]:
        print("\n=== SMTP DESHABILITADO ===")
        print("Para:", recipient)
        print("Asunto:", subject)
        print(body)
        print("=========================\n")
        return True

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = current_app.config["MAIL_FROM"]
    msg["To"] = recipient

    if current_app.config["MAIL_USE_SSL"]:
        server = smtplib.SMTP_SSL(current_app.config["MAIL_SERVER"], current_app.config["MAIL_PORT"])
    else:
        server = smtplib.SMTP(current_app.config["MAIL_SERVER"], current_app.config["MAIL_PORT"])
        if current_app.config["MAIL_USE_TLS"]:
            server.starttls()

    if current_app.config["MAIL_USERNAME"]:
        server.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])

    server.send_message(msg)
    server.quit()
    return True
