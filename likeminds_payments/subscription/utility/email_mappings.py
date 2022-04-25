from utility.states import email_types
from utility.constants import EmailCategories, EmailSubCategories


class EmailMapper:

    mappings = {
        '{}__{}'.format(EmailCategories.CREATE_COMMUNITY, EmailSubCategories.FIRST_PLAN_CREATED): {
            'location': 'cm_onboarding/first_plan_creation_cm_onboarding_email.html',
            'email_type': email_types.ADMIN_EMAIL
        },

        '{}__{}'.format(EmailCategories.JOIN_FLOW, EmailSubCategories.PAYMENT_SUCCESSFUL): {
            'location': 'cash_payments/member_email_member_join.html',
            'email_type': email_types.COMMUNITY_EMAIL
        },

        '{}__{}'.format(EmailCategories.JOIN_FLOW, EmailSubCategories.PAYMENT_SUCCESSFUL_AND_MEMBER_JOINED): {
            'location': 'cash_payments/cm_email_member_join.html',
            'email_type': email_types.ADMIN_EMAIL
        },

        '{}__{}'.format(EmailCategories.SETTLEMENT, EmailSubCategories.SETTLEMENT_SUCCESSFUL_CM): {
            'location': 'settlements/settlement_processed_cm_email.html',
            'email_type': email_types.ADMIN_EMAIL
        },

        '{}__{}'.format(EmailCategories.SETTLEMENT, EmailSubCategories.SETTLEMENT_FAILED_CM): {
            'location': 'settlements/settlement_failed_cm_email.html',
            'email_type': email_types.ADMIN_EMAIL
        },

        '{}__{}'.format(EmailCategories.SETTLEMENT, EmailSubCategories.SETTLEMENT_FAILED_ADMIN): {
            'location': 'settlements/settlement_failed_admin_email.html',
            'email_type': email_types.ADMIN_EMAIL
        },

        '{}__{}'.format(EmailCategories.PAYMENT_PAGE, EmailSubCategories.EMAIL_REPORT): {
            'location': 'all_payment_page_download_report_mail.html',
            'email_type': email_types.ADMIN_EMAIL
        },

        '{}__{}__{}'.format(EmailCategories.PAYMENT_PAGE, EmailSubCategories.EMAIL_REPORT, 2): {
            'location': 'transactions_all_payment_page_download_report_mail.html',
            'email_type': email_types.ADMIN_EMAIL
        },

        '{}__{}__{}'.format(EmailCategories.PAYMENT_PAGE, EmailSubCategories.NEW_PAYMENT, 'member'): {
            'location': 'payment_success_member_email_payment_page.html',
            'email_type': email_types.COMMUNITY_EMAIL
        },

        '{}__{}__{}'.format(EmailCategories.PAYMENT_PAGE, EmailSubCategories.NEW_PAYMENT, 'cm'): {
            'location': 'payment_success_cm_email_payment_page.html',
            'email_type': email_types.ADMIN_EMAIL
        },

        '{}__{}'.format(EmailCategories.PAYMENT_PAGE, EmailSubCategories.FAILED_PAYMENT): {
            'location': 'payment_failed_member_email_payment_page.html',
            'email_type': email_types.COMMUNITY_EMAIL
        },

        '{}__{}'.format(EmailCategories.EVENT_PAYMENT, EmailSubCategories.PAYMENT_SUCCESSFUL): {
            'location': 'event_comms/paid_event_reg_success_non_member.html',
            'email_type': email_types.COMMUNITY_EMAIL
        }
    }

    def get_email_mapping(self, category, subcategory, slug=None):

        if slug:
            return self.mappings.get('{}__{}__{}'.format(category, subcategory, slug))

        return self.mappings.get('{}__{}'.format(category, subcategory), None)


email_mapper = EmailMapper()
