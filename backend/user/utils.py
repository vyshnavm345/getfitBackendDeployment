from django.core.mail import EmailMessage


class Util:
    @staticmethod
    def send_email(data):
        print("sending mail in utils")
        email = EmailMessage(
            subject=data["email_subject"],
            body=data["email_body"],
            to=[data["to_email"]],
        )
        print("message valid", data["email_body"])
        email.send()
