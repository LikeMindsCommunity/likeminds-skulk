from ..email.email_manager import MailManager
from django.core.mail import EmailMultiAlternatives


class MailWrapper(MailManager):

    from_email = 'LikeMinds<hello@likeminds.community>'

    @staticmethod
    def send_email(subject, template, to_mails_list, categories=None, reply_to=None):

        fail_silently = False
        email = EmailMultiAlternatives(
            subject,
            template,
            MailWrapper.from_email,
            to_mails_list,
            reply_to=reply_to
        )
        email.attach_alternative(template, "text/html")

        if categories is not None:
            email.categories = categories

        status = email.send(fail_silently)

        if status == 1:
            return True
        return False
