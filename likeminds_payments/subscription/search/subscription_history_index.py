from django.conf import settings
from django_elasticsearch_dsl import Index, Document, IntegerField, fields, LongField
from django_elasticsearch_dsl_drf.compat import StringField

from elasticsearch_dsl import analyzer, token_filter

from subscription.plans.constants import SUBSCRIPTION_PLAN_NAMES
from subscription.plans.models import SubscriptionPlan
from subscription.subscription_histories.models import SubscriptionHistory
from subscription.subscriptions.constants import LIFETIME_PAYMENT
from subscription.utility.model_utilities import ModelUtilities

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
class SubscriptionHistoryDocument(Document):
    start_date = LongField()
    end_date = LongField()
    description = StringField()
    transaction = fields.ObjectField(
        attr='transaction',
        properties={
            'id': IntegerField(),
            'plan_id': StringField(),
        })
    type = StringField()
    user_id = IntegerField()
    community_id = IntegerField()
    plan_sub_title = StringField()

    class Django(object):
        """Inner nested class Django."""
        model = SubscriptionHistory  # The model associate with this Document
        queryset_pagination = 50

    @staticmethod
    def prepare_plan_sub_title(instance):
        if not instance.transaction:
            return ''

        plan_filter = ModelUtilities.get_model_filter(SubscriptionPlan, {'plan_id': instance.transaction.plan_id})
        if not plan_filter:
            return ''

        plan_instance = plan_filter[0]

        if plan_instance.duration_name == LIFETIME_PAYMENT:
            return '{} for {}'.format(
                plan_instance.cost // 100,
                SUBSCRIPTION_PLAN_NAMES[plan_instance.duration_name]['subtitle']
            )

        else:
            return '{} for {} {}'.format(
                plan_instance.cost // 100,
                plan_instance.duration_in_months,
                SUBSCRIPTION_PLAN_NAMES[plan_instance.duration_name]['subtitle'])
