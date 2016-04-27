from decimal import Decimal


def calculate_fee(amount, posting_type):
    if posting_type == 'offer':
        return amount * Decimal(0.05)
