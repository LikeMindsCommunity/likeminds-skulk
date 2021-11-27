from django.conf import settings
from django_elasticsearch_dsl import Index, Document, IntegerField, fields
from django_elasticsearch_dsl_drf.compat import StringField

from elasticsearch_dsl import analyzer, token_filter

from subscription.plans.constants import SUBSCRIPTION_PLAN_NAMES
from subscription.plans.models import SubscriptionPlan
from subscription.subscriptions.constants import LIFETIME_PAYMENT
from subscription.subscriptions.models import Subscription
from subscription.utility.time_utilities import TimeUtilities

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])

# See Elasticsearch Indices API reference for available settings
INDEX.settings(
    number_of_shards=1,
    number_of_replicas=1
)

html_strip = analyzer(
    'html_strip',
    tokenizer="keyword",
    filter=["lowercase"],
    char_filter=["html_strip"]
)

# creates a reverse index mappings for combinations of words starting from left
# Ref: https://www.elastic.co/guide/en/elasticsearch/guide/current/_index_time_search_as_you_type.htmlg
edge_ngram_completion_filter = token_filter(
    'edge_ngram_completion_filter',
    type="edge_ngram",
    min_gram=1,
    max_gram=20,
)

autocomplete = analyzer(
    'autocomplete',
    tokenizer="standard",
    filter=["lowercase", edge_ngram_completion_filter],
    char_filter=["html_strip"]
)


@INDEX.doc_type
class SubscriptionPlanDocument(Document):
    id = IntegerField(attr='id')
    plan_id = StringField()
    community_id = IntegerField()
    name = StringField()
    duration_name = StringField()
    cost = IntegerField()
    strike_cost = IntegerField()
    duration_in_months = IntegerField()
    plan_sub_title = StringField()
    active_users = fields.ListField(fields.ObjectField(
        properties={
            'id': IntegerField(),
            'joined_since': StringField(),
        }
    ))

    class Django(object):
        """Inner nested class Django."""
        model = SubscriptionPlan  # The model associate with this Document
        queryset_pagination = 50

    @staticmethod
    def prepare_plan_sub_title(instance):
        if instance.duration_name == LIFETIME_PAYMENT:
            return '{} for {}'.format(
                instance.cost // 100,
                SUBSCRIPTION_PLAN_NAMES[instance.duration_name]['subtitle']
            )

        return '{} for {} {}'.format(
            instance.cost // 100,
            instance.duration_in_months,
            SUBSCRIPTION_PLAN_NAMES[instance.duration_name]['subtitle'])

    @staticmethod
    def prepare_active_users(instance):
        active_user_list = list(Subscription.objects.filter(plan_id=instance.plan_id, is_removed=False).exclude(
            user_id=None).values(
            'user_id',
            'date_subscribed'))

        for user in active_user_list:
            if user.get('date_subscribed'):
                user['date_subscribed'] = TimeUtilities.convert_epoch_to_month_year_format(user.get('date_subscribed'))

        return active_user_list
