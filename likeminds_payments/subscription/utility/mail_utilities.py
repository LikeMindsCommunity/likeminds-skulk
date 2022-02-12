from django.conf import settings

from subscription.utility.constants import MAIL_CATEGORY_BETA, MAIL_CATEGORY_PROD


class MailUtilities:

    @staticmethod
    def get_email_category_list_using_category_subcategory(category, subcategory):
        categories = []
        environment = MAIL_CATEGORY_BETA if settings.IS_BETA else MAIL_CATEGORY_PROD
        categories.append(environment)
        categories.append(f'{environment} - {category}')
        categories.append(f'{environment} - {category} - {subcategory}')
        return categories
