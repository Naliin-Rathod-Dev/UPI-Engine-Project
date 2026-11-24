import random as rd
from validation import require_pin
from models import UPIUsers, Transaction
import logging

logger = logging.getLogger(__name__)


class UPI_Central_System():

    """ Central UPI System """

    def __init__(self):

        # Store of registered upi users
        self.registered_users = {}

    def _generate_id(self, suffix):
        # Generate the unique Central id (UPI) & Bank id (e.g. for SBI @ybl)

        while True:
            raw_id = rd.randint(100000000,200000000)
            unique_id = f"{raw_id}@{suffix}"

            if unique_id not in self.registered_users:
                return unique_id

    def __len__(self):
        return len(self.registered_users)

    def __str__(self):
        return f"{self.registered_users}"
        

class PhonePe(UPI_Central_System):
    # PhonePe app connected to UPI Central System

    def __init__(self):
        super().__init__()
        self.app_name = "PhonePe"
        self.app_users = [] # Store of app users
        self.transactions = [] # Store of users transactions

    def create_user(self, name, mobile, bank, pin, balance=0):
        # User creation from the app

        if not name or not mobile or not bank or not pin:
            logger.error("Didn't found 'name', 'mobile', 'bank' or 'pin'!")
            raise ValueError({"Nessage": "Name, Mobile, Bank and pin are mandatory."})

        pass_len = len(str(abs(pin)))

        if pass_len < 4 or pass_len > 4:
            logger.error('Minimum/Maximum pin length error')
            raise ValueError("Pin length should be 4.")

        user = UPIUsers(name,mobile,bank,pin,balance)

        user.app = self.app_name

        user.upi_id = self._generate_id("upi")
        user.phonepe_id = self._generate_id("ybl")

        self.registered_users[user.upi_id] = user
        self.registered_users[user.phonepe_id] = user

        self.app_users.append(user)

        logger.info("User's account created successfully, Welcome %s!" % user.username)

        return user

    @require_pin
    def make_payment(self, sender_handle, receiver_handle, amount, pin):
        # Payment to different users from the app

        sender = self.registered_users.get(sender_handle) # Validate sender
        receiver = self.registered_users.get(receiver_handle) # Validate receiver

        if not receiver:
            logger.error("Receiver's handle not found! | Receiver's Handle: %s" % receiver)
            raise PermissionError("Invalid receiver's handle, Try again!")

        if amount <= 0:
            logger.error("Negative or Zero amount was tried to to transfer!")
            raise ValueError("Amount must be greater than 0")

        if sender.balance < amount:
            self.transactions.append(
                Transaction(
                    sender_handle=sender, receiver_handle=receiver, amount=amount, status="FAILED: Insufficient Funds!"
                )
            )
            
            logger.error("Insufficient Balance amount in the Bank!")
            raise ValueError("Insufficient Balance, Try again...")

        sender.balance -= amount
        receiver.balance += amount

        txn = Transaction(sender_handle=sender_handle, receiver_handle=receiver_handle, amount=amount, status="SUCCESS")
        self.transactions.append(txn)

        logger.info("Transaction successful! Amount ₹%d transfered to [Name: %s] [UPI ID: %s]" , amount, receiver.username, receiver.upi_id)
        return txn


    def check_transaction_history(self, user_handle,min_amount=0, status_filter=None):

        v_user_handle = self.registered_users.get(user_handle)

        if not v_user_handle:
            logger.error("User Handle not found error! [Handle: %s]" , (user_handle))
            raise PermissionError("User handle does not exist!, Try again")
        """
        if str(pin) != v_user_handle.pin:
            logger.warning("Incorrect pin entered by user handle: [%s]" % (v_user_handle))
            raise PermissionError("Incorrect pin entered, Try again!")
        """
        user_handles = {v_user_handle.upi_id, v_user_handle.phonepe_id}

        for txns in self.transactions:
            is_involved = txns.sender_handle in user_handles or txns.receiver_handle in user_handles
            meets_amount = txns.amount >= min_amount
            meets_status = (status_filter is None) or (txns.status == status_filter)

            if is_involved and meets_amount and meets_status:
                yield txns

        

    @require_pin
    def check_balance(self, user_handle, pin):

        validate_user_handle = self.registered_users.get(user_handle)

        if not validate_user_handle:
            logger.error("Invalid/Unregistered user handle's balance was requested! | User Handle: %s" % (validate_user_handle))
            raise PermissionError("User's id not found!")

        statement = f"""
------------- Balance Statement ---------------

Current Balance: ₹{validate_user_handle.balance}
-----------------------------------------------
"""
        logger.info("Balance statement requested and received by [UPI ID: %s]" % (user_handle))
        return statement