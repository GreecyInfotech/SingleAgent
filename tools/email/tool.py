from pydantic import BaseModel, EmailStr


class EmailMessage(BaseModel):
    to: list[EmailStr]
    subject: str
    body: str
    cc: list[EmailStr] = []
    html: bool = False


class EmailTool:
    async def send(self, message: EmailMessage) -> dict:
        return {
            "status": "sent",
            "message_id": "msg-001",
            "recipients": [str(e) for e in message.to],
            "subject": message.subject,
        }

    async def send_template(
        self, template: str, to: list[str], variables: dict
    ) -> dict:
        return {
            "status": "sent",
            "template": template,
            "recipients": to,
            "variables": variables,
        }
