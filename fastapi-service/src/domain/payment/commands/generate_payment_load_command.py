from dataclasses import dataclass

@dataclass
class GeneratePaymentLoadCommand:
    num_requests: int = 10000
    user_id: int = 1
    account_id: int = 1