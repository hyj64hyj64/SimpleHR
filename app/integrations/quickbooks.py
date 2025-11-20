from urllib.parse import urlencode
from typing import Optional
from ..core.config import settings


QB_AUTH_BASE = "https://appcenter.intuit.com/connect/oauth2"


def get_qb_authorization_url(state: str = "simple-hr") -> str:
    """
    Build QuickBooks Online OAuth2 authorization URL.
    You will redirect the browser to this URL.
    """
    if not (settings.qb_client_id and settings.qb_redirect_uri):
        raise RuntimeError("QuickBooks client_id/redirect_uri not configured")

    params = {
        "client_id": settings.qb_client_id,
        "redirect_uri": settings.qb_redirect_uri,
        "response_type": "code",
        "scope": "com.intuit.quickbooks.accounting com.intuit.quickbooks.payroll",
        "state": state,
    }
    return f"{QB_AUTH_BASE}?{urlencode(params)}"


# 🔹 These functions are stubs – you will fill in real HTTP calls later.
# They are here only to show structure & keep your app compile-safe.

def exchange_code_for_tokens(auth_code: str, realm_id: Optional[str] = None):
    """
    TODO: Implement HTTP POST to QuickBooks token endpoint.
    Should return access_token, refresh_token, expiry.
    """
    # Placeholder structure
    return {
        "access_token": "fake-access-token",
        "refresh_token": "fake-refresh-token",
        "expires_in": 3600,
        "realm_id": realm_id,
    }


def refresh_qb_tokens(refresh_token: str):
    """
    TODO: Implement token refresh call here.
    """
    return {
        "access_token": "refreshed-access-token",
        "refresh_token": "refreshed-refresh-token",
        "expires_in": 3600,
    }


def sync_employees_to_quickbooks(session):
    """
    TODO: use session to read Employee objects and push to QuickBooks via API.
    """
    # This is just scaffolding – no real logic yet.
    pass


def sync_timesheets_to_quickbooks(session):
    """
    TODO: use session to read Timesheet objects and push time data to QuickBooks.
    """
    pass
