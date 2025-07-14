# tests/unit/test_business_logic.py

import pytest
from core.constants import L1_REFERRAL_COMMISSION_PERCENT, L2_REFERRAL_COMMISSION_PERCENT

# This is a placeholder for a real function if you had one.
# For now, we'll test the logic directly.
def calculate_commissions(payment_amount_rub: int) -> tuple[int, int]:
    l1_commission = int(payment_amount_rub * (L1_REFERRAL_COMMISSION_PERCENT / 100))
    l2_commission = int(payment_amount_rub * (L2_REFERRAL_COMMISSION_PERCENT / 100))
    return l1_commission, l2_commission

@pytest.mark.parametrize("amount, expected_l1, expected_l2", [
    (10000, 3000, 500), # 100 RUB
    (9900, 2970, 495),  # 99 RUB
    (3000, 900, 150),   # 30 RUB
    (0, 0, 0),
])
def test_calculate_commissions(amount, expected_l1, expected_l2):
    """Unit test for the referral commission calculation logic."""
    l1, l2 = calculate_commissions(amount)
    assert l1 == expected_l1
    assert l2 == expected_l2
