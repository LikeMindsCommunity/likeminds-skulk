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
    'failed': SettlementStatus.FAILED
}
VALID_PAYOUT_WEBHOOK_EVENTS = [
    "payout.queued",
    "payout.initiated",
    "payout.processed",
    "payout.updated",
    "payout.reversed",
    "payout.failed"
]
SETTLEMENTS_PAGE_SIZE = 50
