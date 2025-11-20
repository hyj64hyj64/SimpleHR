from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from ..integrations.quickbooks import get_qb_authorization_url, exchange_code_for_tokens

router = APIRouter(prefix="/quickbooks", tags=["quickbooks"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/connect")
def qb_connect():
    """
    Redirect user to QuickBooks OAuth authorization page.
    """
    auth_url = get_qb_authorization_url()
    return RedirectResponse(auth_url)


@router.get("/callback")
def qb_callback(request: Request, code: Optional[str] = None, realmId: Optional[str] = None, state: Optional[str] = None):
    """
    QuickBooks redirects back here with ?code=...&realmId=...
    For now we just show them on a page as a stub.
    """
    if not code:
        return templates.TemplateResponse(
            "quickbooks_status.html",
            {"request": request, "status": "Missing authorization code"},
        )

    token_data = exchange_code_for_tokens(code, realm_id=realmId)

    # 🔹 In a real implementation you would save token_data into DB.
    return templates.TemplateResponse(
        "quickbooks_status.html",
        {
            "request": request,
            "status": "Connected (stub only)",
            "token_data": token_data,
            "realm_id": realmId,
            "state": state,
        },
    )
