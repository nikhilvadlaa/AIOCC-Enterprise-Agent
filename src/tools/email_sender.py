class EmailSender:
    def __init__(self):
        self.logger = None
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
        print(f"\n=== EMAIL MOCK ===")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print(f"===================\n")
        return True