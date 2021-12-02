import enum


class SearchIndices(enum.Enum):
    SUBSCRIPTION_PLAN = "subscription_plan"
    SUBSCRIPTION_HISTORY = "subscription_history"


SUBSCRIPTION_PLAN_SUB_TITLE_FIELD = "plan_sub_title"

SUBSCRIPTION_PLAN_SUPPORTED_SEARCH_FIELDS = [SUBSCRIPTION_PLAN_SUB_TITLE_FIELD]
