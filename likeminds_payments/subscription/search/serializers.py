from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from .subscription_plan_index import SubscriptionPlanDocument


class SubscriptionPlanDocumentSerializer(DocumentSerializer):
    """Serializer for the Subscription Plan document."""

    class Meta:
        """Meta options."""
        document = SubscriptionPlanDocument
        fields = '__all__'

    def to_representation(self, obj):
        data = super(SubscriptionPlanDocumentSerializer, self).to_representation(obj)

        fields = self._readable_fields

        for field in fields:

            if data[field.field_name] is None:
                del data[field.field_name]

        return data

