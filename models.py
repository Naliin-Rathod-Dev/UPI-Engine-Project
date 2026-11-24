import uuid
from datetime import datetime

class UPIUsers():
    def __init__(self, username, mobile, bank, pin, balance=0):

        """ The data of an individual user. """

        self.username = username
        self.mobile = mobile
        self.app = None
        self.bank = bank
        self.pin = str(pin)
        self.balance = balance

        self.upi_id = None
        self.phonepe_id = None

        self.locked_until = None
        self.failed_attempts = 0

    def __str__(self):
        return f'User({self.username}, {self.mobile}, {self.app}, {self.bank}, {self.balance},)'

    def __repr__(self):
        return f'User_Dev({self.username}, {self.mobile}, {self.app}, {self.bank}, {self.pin}, {self.balance})'

    def __eq__(self, value):

        if not isinstance(value, UPIUsers):
            return NotImplemented

        return (
            self.upi_id == value.upi_id and
            self.phonepe_id == value.phonepe_id
        )


class Transaction():

    def __init__(self, sender_handle, receiver_handle, amount, status="SUCCESS"):

        self.txn_id = f"TXN{uuid.uuid4().hex[:8].upper()}"
        self.sender_handle = sender_handle
        self.receiver_handle = receiver_handle
        self.amount = amount
        self.status = status
        self.timestamp = datetime.now()

    def __str__(self):
        time_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return str(f"\n[{time_str}] {self.txn_id} | {self.sender_handle} -> {self.receiver_handle} | Amount: {self.amount} | Status: {self.status}")

    def __repr__(self):
        return str(f"Transaction(id={self.txn_id}, amount={self.amount}, status={self.status}")