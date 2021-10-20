from rest_framework import serializers
from ..payment_page.models import PaymentPageMeta


class PaymentPageMetaSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentPageMeta
        fields = ('id', 'payment_page_id', 'title', 'description', 'amount_type', 'amount',
                  'custom_success_message', 'redirect_url', 'community_id', 'is_active', 'contact_email',
                  'contact_mobile_no', 'created_at', 'updated_at')

    def __init__(self, *args, **kwargs):
        super(PaymentPageMetaSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, community):
        data = super(PaymentPageMetaSerializer, self).to_representation(community)

        fields = self._readable_fields

        for field in fields:

            if data[field.field_name] is None:
                del data[field.field_name]

        return data
