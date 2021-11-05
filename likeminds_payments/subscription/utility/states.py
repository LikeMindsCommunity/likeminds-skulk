class EventDiscountType:
    PERCENTAGE = 0
    FLAT = 1


class TransactionType:
    COMMUNITY_SUBSCRIPTION = 0
    EVENT = 1
    PAYMENT_PAGE = 2


class DocType:
    AADHAR = 0
    DRIVING_LICENCE = 1
    PASSPORT = 2
    VOTER_ID = 3
    OTHER = 4


class KYCState:
    PENDING_APPROVAL = 0
    APPROVED = 1
    INACTIVE = 2


class MemberState:
    GUEST = 0
    ADMIN = 1
    MEMBER = 4
    PROFILE_UNAVAILABLE = 9
    PENDING_MEMBER = 3


class TransactionStatusType:
    CAPTURED = 'captured'
    REFUND = 'refund'
    FAILED = 'failed'


class CohortTypes:
    NORMAL = 0
    SUBSCRIPTION_PLAN = 1
    SUBSCRIPTION_EXPIRED_PLAN = 2
    ALL_MEMBER = 3


cohort_types = CohortTypes()

cohort_type_list = [cohort_types.NORMAL, cohort_types.SUBSCRIPTION_PLAN,
                    cohort_types.SUBSCRIPTION_EXPIRED_PLAN, cohort_types.ALL_MEMBER]
