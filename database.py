import logging
from pathlib import Path
import sqlite3

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database"
DB_DIR.mkdir(exist_ok=True)
DB_FILE_PATH = DB_DIR / "upi_database.db"

def get_connection():
    """Creates the users and transactions tables if they do not already exist."""

    conn = sqlite3.connect(DB_FILE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        "PRAGMA foreign_keys = ON;"
    )
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXIST users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            mobile TEXT UNIQUE NOT NULL,
            app TEXT NOT NULL,
            bank TEXT NOT NULL,
            pin TEXT NOT NULL, 
            balance REAL NOT NULL DEFAULT 0.0 CHECK (balance>=0), 
            upi_id TEXT UNIQUE NOT NULL,
            phonepe_id TEXT UNIQUE NOT NULL,
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until TEXT
            );
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXIST transactions (
            txn_id TEXT PRIMARY KEY,
            sender_handle TEXT NOT NULL,
            receiver_handle TEXT NOT NULL,
            amount REAL NOT NULL CHECK (amount>0),
            status TEXT NOT NULL,
            timestamp TEXT NOT NULL
            )
            """
        )

        logger.info("Database initialized at %s", DB_FILE_PATH)

def fetch_user_by_handle(handle: str):
    """Finds a user matching either their @upi or @ybl handle."""

    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM users WHERE upi_id = ? OR phonepe_id = ?",
            (handle,handle)
        )

        return cursor.fetchone()

def execute_transfer(sender_handle: str, receiver_handle: str, amount: float, txn_id: str, timestamp: str):
    """
    Executes debit, credit, and ledger logging inside a single ACID transaction.
    If any step fails, all changes roll back automatically.
    """

    with get_connection() as conn:
        # Debit sender (only if sufficient balance exists)

        cursor = conn.execute(
            "UPDATE users SET balance = balance - ? WHERE upi_id = ? OR phonepe_id = ? AND balance >= ?",
            (amount,sender_handle,sender_handle,amount)
        )

        if cursor.rowcount == 0:
            raise ValueError("Insufficient balance OR sender not found.")

        # Credit receiver
        cursor = conn.execute(
            "UPDATE users SET balance = balance + ? WHERE upi_id = ? OR phonepe_id = ?",
            (amount,sender_handle,sender_handle)
        )

        if cursor.rowcount == 0:
            raise ValueError("Receiver not found.")

        # Record transaction in ledger 
        conn.execute(
            """
            INSERT INTO transactions (txn_id, sender_handle, receiver_handle, amount, status, timestamp),
            VALUES (?,?,?,?,"SUCCESS",?)
            """,
            (txn_id, sender_handle, receiver_handle, amount, timestamp)
        )

