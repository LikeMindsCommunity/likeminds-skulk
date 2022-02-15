from ..utility.states import SettlementStatus

PAYOUT_MODE = 'NEFT'
PAYOUT_PURPOSE = 'payout'
PAYOUT_NARRATION = 'LikeMindsPayout'
PAYOUT_QUEUE = True
PAYOUT_STATUS_MAP = {
    'queued': SettlementStatus.QUEUED,
    'processing': SettlementStatus.INITIATED,
    'processed': SettlementStatus.PROCESSED,
    'reversed': SettlementStatus.REVERSED,
    'failed': SettlementStatus.FAILED,
    'started': SettlementStatus.STARTED
}
VALID_PAYOUT_WEBHOOK_EVENTS = [
    "payout.queued",
    "payout.initiated",
    "payout.processed",
    "payout.updated",
    "payout.reversed",
    "payout.failed"
]
SETTLEMENT_STATUS_MAP_FOR_EMAIL = {
    SettlementStatus.REVERSED: 'REVERSED',
    SettlementStatus.FAILED: 'FAILED',
    SettlementStatus.QUEUED: 'QUEUED',
    SettlementStatus.INITIATED: 'INITIATED',
    SettlementStatus.PROCESSED: 'PROCESSED'
}
SETTLEMENTS_PAGE_SIZE = 50
SETTLEMENT_PROCESSED_EMAIL_TO_CM_SUBJECT = "Settlement processed for {} on {}"
SETTLEMENT_FAILED_EMAIL_TO_CM_SUBJECT = "Settlement failed for {} on {}"
STARTED_SETTLEMENT_STATUS = 'started'
