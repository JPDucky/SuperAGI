from typing import Type
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config
import imaplib
from superagi.helper.imap_email import ImapEmail
import smtplib
import time
import os
import mimetypes
from email.header import decode_header
from email.message import EmailMessage

class SendEmailAttachmentInput(BaseModel):
    to: str = Field(..., description="Email Address of the Receiver, default email address is 'example@example.com'")
    subject: str = Field(..., description="Subject of the Email to be sent")
    body: str = Field(..., description="Email Body to be sent")
    filename: str = Field(..., description="Name of the file to be sent as an Attachement with Email")

class SendEmailAttachmentTool(BaseTool):
    name: str = "Send Email with Attachement"
    args_schema: Type[BaseModel] = SendEmailAttachmentInput
    description: str = "Send an Email with a file attached to it"
    
    def _execute(self, to: str, subject: str, body: str, filename: str) -> str:
        base_path = get_config('EMAIL_ATTACHMENT_BASE_PATH')
        if not base_path:
            base_path = ""
        base_path = base_path + filename
        attachement_path = base_path
        attachement = os.path.basename(attachement_path)
        return self.send_email_with_attachement(to,subject,body,attachement_path,attachement)
    
    def send_email_with_attachement(self, to, subject, body, attachement_path, attachement) -> str:
        email_sender = get_config('EMAIL_ADDRESS')
        email_password = get_config('EMAIL_PASSWORD')
        if email_sender == "" or email_sender.isspace():
            return "Error: Email Not Sent. Enter a valid Email Address."
        if email_password == "" or email_password.isspace():
            return "Error: Email Not Sent. Enter a valid Email Password."
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = email_sender
        message["To"] = to
        signature = get_config('EMAIL_SIGNATURE')
        if signature:
            body += f"\n{signature}"
        message.set_content(body)
        if attachement_path:
            ctype, encoding = mimetypes.guess_type(attachement_path)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"
            maintype, subtype = ctype.split("/",1)
            with open(attachement_path, "rb") as file:
                message.add_attachment(file.read(),maintype=maintype, subtype=subtype, filename=attachement)
        draft_folder = get_config('EMAIL_DRAFT_MODE_WITH_FOLDER')
        
        if message["To"] == "example@example.com" or draft_folder:
            conn = ImapEmail().imap_open(draft_folder, email_sender, email_password)
            conn.append(
                draft_folder,
                "",
                imaplib.Time2Internaldate(time.time()),
                str(message).encode("UTF-8")
            )
            return f"Email went to {draft_folder}"
        else:
            smtp_host = get_config('EMAIL_SMTP_HOST')
            smtp_port = get_config('EMAIL_SMTP_PORT')
            with smtplib.SMTP(smtp_host,smtp_port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(email_sender,email_password)
                smtp.send_message(message)
                smtp.quit()
            return f"Email was sent to {to}"



