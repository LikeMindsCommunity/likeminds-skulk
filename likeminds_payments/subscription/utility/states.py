class EventDiscountType:
    PERCENTAGE = 0
    FLAT = 1


class TransactionType:
    COMMUNITY_SUBSCRIPTION = 0
    EVENT = 1
    PAYMENT_PAGE = 2


class MemberState:
    GUEST = 0
    ADMIN = 1
    MEMBER = 4
    PROFILE_UNAVAILABLE = 9
    PENDING_MEMBER = 3


class CohortTypes:
    NORMAL = 0
    SUBSCRIPTION_PLAN = 1
    SUBSCRIPTION_EXPIRED_PLAN = 2
    ALL_MEMBER = 3


cohort_types = CohortTypes()

cohort_type_list = [cohort_types.NORMAL, cohort_types.SUBSCRIPTION_PLAN,
                    cohort_types.SUBSCRIPTION_EXPIRED_PLAN, cohort_types.ALL_MEMBER]
