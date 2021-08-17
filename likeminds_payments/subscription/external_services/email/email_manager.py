import abc


class MailManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'send_email') and callable(subclass.create_user)) and
                (hasattr(subclass, 'send_email_with_attachment') and callable(subclass.create_event)) or
                NotImplemented)

    @staticmethod
    def send_email(subject, template, to_mails_list, categories=None, reply_to=None):
        """
        sends email
        """
        raise NotImplementedError

    @staticmethod
    def send_email_with_attachment(subject, template, to_mails_list, attachment_list, categories=None, reply_to=None):
        """
        sends email with attachment file
        """
        raise NotImplementedError
