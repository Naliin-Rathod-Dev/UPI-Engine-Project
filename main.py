import logging
from app import PhonePe

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("upi_log.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("UPI ENGINE")

app = PhonePe()
user1 = app.create_user("Edson Averio",7770011686,"SBI",1234,41000)
user2 = app.create_user("Pele dos Santos", 8805011804,"HDFC", 4000,4000)
user3 = app.create_user(
    name="Naliin Rathod", mobile=8805011804, bank="Axis Bank", pin=9402, balance=12000
)

# Incorrect attempt 1

try:
    p1 = app.make_payment(
    user1.phonepe_id,
    user2.upi_id,
    7000,
    1234
    )

    balance_statement = app.check_balance(
        user1.upi_id,
        1234
    )

    print(p1)

except PermissionError as e:
    print(f"Error occured: {e}")


try:
    p2 = app.make_payment(
    user1.phonepe_id,
    user2.upi_id,
    800,
    1234
    )

    balance_statement = app.check_balance(
        user1.upi_id,
        1234
    )

    print(p1)

except PermissionError as e:
    print(f"Error occured: {e}")

try:
    print("\n---------------- List of Transactions -----------------")
    for txn in app.check_transaction_history(user_handle=user1.upi_id):
        print(txn)

except PermissionError as e:
    print(f'Error occured: {e}')