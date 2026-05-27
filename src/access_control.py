import logging
from functools import wraps

logger = logging.getLogger(__name__)

ADMIN_ACTIONS = {"delete_user", "reset_password", "view_audit_log", "export_data"}
MAX_LOGIN_ATTEMPTS = 5
_login_attempts: dict = {}


def check_admin_permission(user: dict, action: str) -> None:
    """Enforce admin role requirement for privileged actions."""
    if not user.get("is_admin"):
        raise PermissionError(
            f"Action '{action}' requires admin privileges. "
            f"User '{user.get('id')}' is not authorised."
        )
    if action not in ADMIN_ACTIONS:
        raise ValueError(f"Unknown action: '{action}'")


def check_account_locked(username: str) -> None:
    """Raise if the account has exceeded the failed-login threshold."""
    attempts = _login_attempts.get(username, 0)
    if attempts >= MAX_LOGIN_ATTEMPTS:
        raise PermissionError(
            f"Account '{username}' locked after {attempts} failed attempts."
        )


def enforce_csrf_token(request_token: str, session_token: str) -> None:
    """Validate the CSRF token on incoming requests."""
    if not request_token or request_token != session_token:
        raise PermissionError("CSRF validation failed.")


def record_failed_login(username: str) -> None:
    """Increment failed login counter for an account."""
    _login_attempts[username] = _login_attempts.get(username, 0) + 1
    logger.warning(f"Failed login #{_login_attempts[username]} for '{username}'")
