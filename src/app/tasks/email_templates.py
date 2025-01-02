from email.message import EmailMessage
from src.app.core.config import settings


def create_confirmation_template(
        user: dict,
) -> EmailMessage:
    email = EmailMessage()

    email["Subject"] = "Подтверждение регистрации"
    email["From"] = settings.email
    email["To"] = user['email']

    email.set_content(
        f"""
            <h1>Подтвердить регистрацию</h1>
             Вы зарегестрировались, {user['name']} 
        """,
        subtype="html")
    return email
