from rest_framework import serializers
from .models import CommunityKYC


class KycSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommunityKYC
        fields = ('id', 'user_id', 'community_id', 'name', 'address', 'doc_type', 'doc_number', 'doc_front_url',
                  'doc_back_url', 'doc_pan_number', 'doc_pan_url', 'gstn', 'bank_user_name', 'bank_ifsc_code',
                  'account_number', 'bank_name', 'status', 'contact_id', 'account_id', 'created_at', 'updated_at')
