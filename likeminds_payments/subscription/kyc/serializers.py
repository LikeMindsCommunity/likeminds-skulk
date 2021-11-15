from rest_framework import serializers
from .models import CommunityKYC


class KycSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommunityKYC
        fields = ('id', 'user_id', 'community_id', 'name', 'address', 'doc_type', 'doc_number', 'doc_front_url',
                  'doc_back_url', 'doc_pan_number', 'doc_pan_url', 'gstn', 'bank_user_name', 'bank_ifsc_code',
                  'account_number', 'bank_name', 'status', 'contact_id', 'account_id', 'created_at', 'updated_at')

    def update(self, kyc_instance, validated_data):
        kyc_instance.name = validated_data.get('name', kyc_instance.name)
        kyc_instance.address = validated_data.get('address', kyc_instance.address)
        kyc_instance.doc_type = validated_data.get('doc_type', kyc_instance.doc_type)
        kyc_instance.doc_number = validated_data.get('doc_number', kyc_instance.doc_number)
        kyc_instance.doc_front_url = validated_data.get('doc_front_url', kyc_instance.doc_front_url)
        kyc_instance.doc_back_url = validated_data.get('doc_back_url', kyc_instance.doc_back_url)
        kyc_instance.doc_pan_number = validated_data.get('doc_pan_number', kyc_instance.doc_pan_number)
        kyc_instance.doc_pan_url = validated_data.get('doc_pan_url', kyc_instance.doc_pan_url)
        kyc_instance.gstn = validated_data.get('gstn', kyc_instance.gstn)
        kyc_instance.bank_user_name = validated_data.get('bank_user_name', kyc_instance.bank_user_name)
        kyc_instance.bank_ifsc_code = validated_data.get('bank_ifsc_code', kyc_instance.bank_ifsc_code)
        kyc_instance.account_number = validated_data.get('account_number', kyc_instance.account_number)
        kyc_instance.bank_name = validated_data.get('bank_name', kyc_instance.bank_name)
        kyc_instance.status = validated_data.get('status', kyc_instance.status)
        kyc_instance.save()

        return kyc_instance
