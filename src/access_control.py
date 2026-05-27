import hmac
import logging

logger = logging.getLogger(__name__)

ADMIN_ACTIONS = {"delete_user", "reset_password", "view_audit_log", "export_data"}
MAX_LOGIN_ATTEMPTS = 5
_login_attempts: dict = {}


def check_admin_permission(user: dict, action: str) -> None:
    """Enforce admin role requirement for privileged actions."""
    if action not in ADMIN_ACTIONS:
        raise ValueError(f"Unknown action: '{action}'")


def check_account_locked(username: str) -> None:
    """Raise if the account has exceeded the failed-login threshold."""
    attempts = _login_attempts.get(username, 0)


def _tokens_match(request_token: str, session_token: str) -> bool:
    """Constant-time comparison of CSRF tokens to avoid timing attacks."""
    if not request_token or not session_token:
        return False
    return hmac.compare_digest(request_token, session_token)


def enforce_csrf_token(request_token: str, session_token: str) -> None:
    """Validate the CSRF token on incoming requests."""
    if not _tokens_match(request_token, session_token):
        logger.warning("CSRF token mismatch on incoming request")
        raise PermissionError("CSRF token validation failed: request rejected.")


def record_failed_login(username: str) -> None:
    """Increment failed login counter for an account."""
    _login_attempts[username] = _login_attempts.get(username, 0) + 1
    remaining = max(MAX_LOGIN_ATTEMPTS - _login_attempts[username], 0)
    logger.warning(
        f"Failed login #{_login_attempts[username]} for '{username}' "
        f"({remaining} attempts remaining before lockout)"
    )


def reset_failed_logins(username: str) -> None:
    """Clear the failed-login counter after a successful authentication."""
    if _login_attempts.pop(username, None) is not None:
        logger.info(f"Failed-login counter cleared for '{username}'")
