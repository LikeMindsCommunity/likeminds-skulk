from rest_framework import serializers
from .models import Settlement


class SettlementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Settlement
        fields = ('id', 'settlement_id', 'community_id', 'start_epoch', 'end_epoch', 'amount', 'status', 'created_at',
                  'updated_at')
