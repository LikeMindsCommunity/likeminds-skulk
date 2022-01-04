def TransactionSerializer(transactions) -> list:

    output = []

    for transaction in transactions:
        transaction_object = {
            'id': transaction.id,
            'plan_id': transaction.plan_id,
            'payment_id': transaction.payment_id,
            'community_name': transaction.community_name,
            'plan_name': transaction.plan_name,
            'plan_cost': transaction.plan_cost,
            'renew': transaction.renew,
            'amount': transaction.amount,
            'payment_email': transaction.payment_email,
            'payment_phone': transaction.payment_phone,
            'currency': transaction.currency,
            'is_international': transaction.is_international,
            'method': transaction.method,
            'status': transaction.status,
            'error_description': transaction.error_description,
            'refund_amount': transaction.refund_amount,
            'user_id': transaction.user_id,
            'payment_page_url': transaction.payment_page_url,
            'shared_by': transaction.shared_by,
            'grace_period': transaction.grace_period,
            'type': transaction.type,
            'type_id': transaction.type_id,
            'created_at': transaction.created_at,
            'payment_name': transaction.payment_name,
            'settlement_id': transaction.settlement_id,
            'refund_handled': transaction.refund_handled
        }

        output.append(transaction_object)

    return output
