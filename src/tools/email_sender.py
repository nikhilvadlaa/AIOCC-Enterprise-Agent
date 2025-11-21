import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class EmailSender:
    def __init__(self):
        self.logger = None
        self.api_key = os.environ.get("SENDGRID_API_KEY")
        self.default_from = os.environ.get("SENDGRID_FROM_EMAIL", "noreply@example.com")

    def attach_logger(self, logger):
        self.logger = logger

    def send_email(self, to, subject, body, trace_id=None):
        if self.logger:
            self.logger.log(
                message=f"Sending email to {to} with subject: {subject}",
                level="INFO",
                agent="EmailSender",
                trace_id=trace_id if 'trace_id' in locals() else None
            )
        
        if self.api_key:
            message = Mail(
                from_email=self.default_from,
                to_emails=to,
                subject=subject,
                html_content=body
            )
            try:
                sg = SendGridAPIClient(self.api_key)
                response = sg.send(message)
                print(f"[EMAIL REAL] Sent to {to}. Status: {response.status_code}")
                return True
            except Exception as e:
                print(f"[EMAIL ERROR] {e}")
                return False
        else:
            print(f"\n=== EMAIL MOCK ===")
            print(f"To: {to}")
            print(f"Subject: {subject}")
            print(f"Body:\n{body}")
            print(f"===================\n")
            return True