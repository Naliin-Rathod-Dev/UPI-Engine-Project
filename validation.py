from functools import wraps
import inspect
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def require_pin(func):
    
    sig = inspect.signature(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        
        bound = sig.bind(*args,**kwargs)
        bound.apply_defaults()

        arguments = bound.arguments

        self = arguments.get('self')
        user_handle_or_sender_handle = arguments.get('user_handle') or arguments.get('sender_handle')
        pin = arguments.get('pin')

        user = self.registered_users.get(user_handle_or_sender_handle)

        if not user:
            logger.error('User handle not found: %s' % (user_handle_or_sender_handle))
            raise PermissionError("Sender/User not found!")

        if not hasattr(user, "pin") or user.pin is None:
            logger.error(
                'PIN was not set: [UPI ID; %s]' % (user.upi_id)
            )
            raise PermissionError("There is no pin set")

        now = datetime.now()

        if user.locked_until:
            if now < user.locked_until:
                remaining_time = user.lock_until - now
                hours = int(remaining_time.total_seconds() // 3600)
                minutes = int((remaining_time.total_seconds % 3600) // 60)
                logger.critical("All 3 attempts failed, User Handle: %s | locked for 24 hours | Time remaining: %shrs and %smins" % (user.upi_id, hours, minutes))
                raise PermissionError(
                    f"Account locked due to 3 failed attempts. Try again in {hours}hrs and {minutes}mins"
                )

            else:
                user.locked_until = None
                user.failed_attempts = 0

        if str(user.pin) != str(pin):
            user.failed_attempts+=1
            remaining_attempts = 3 - user.failed_attempts

            if user.failed_attempts >= 3:
                user.locked_until = now + timedelta(hours=24)
                logger.critical("All 3 attempts failed for %s | Account locked for 24 hours" % (user.upi_id))
                raise PermissionError(
                    f"Maximum 3 attempts reached! Account locked for 24 hours"
                )

            logger.warning("Incorrect pin entered by [UPI ID: %s] and [Attempts remaining: %d]" % (user.upi_id, remaining_attempts))
            raise PermissionError(f"Incorrect pin entered, {remaining_attempts} attempts left!")

        user.failed_attempts = 0

        return func(*args, **kwargs)

    return wrapper


