def KycSerializer(kyc_instance) -> dict:

    kyc_object = {
        'id': kyc_instance.id,
        'user_id': kyc_instance.user_id,
        'community_id': kyc_instance.community_id,
        'name': kyc_instance.name,
        'address': kyc_instance.address,
        'doc_type': kyc_instance.doc_type,
        'doc_number': kyc_instance.doc_number,
        'doc_front_url': kyc_instance.doc_front_url,
        'doc_back_url': kyc_instance.doc_back_url,
        'doc_pan_number': kyc_instance.doc_pan_number,
        'doc_pan_url': kyc_instance.doc_pan_url,
        'gstn': kyc_instance.gstn,
        'bank_user_name': kyc_instance.bank_user_name,
        'bank_ifsc_code': kyc_instance.bank_ifsc_code,
        'account_number': kyc_instance.account_number,
        'bank_name': kyc_instance.bank_name,
        'status': kyc_instance.status,
        'contact_id': kyc_instance.contact_id,
        'account_id': kyc_instance.account_id,
        'created_at': kyc_instance.created_at,
        'updated_at': kyc_instance.updated_at
    }

    return kyc_object


def MultipleKycSerializer(kyc_instances) -> list:

    output = []

    for kyc_instance in kyc_instances:
        output.append(KycSerializer(kyc_instance))

    return output
