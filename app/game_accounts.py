"""Link gaming identities to the current signed-in user."""

from datetime import datetime, timezone
import logging
import os
import re
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
import httpx
from starlette.concurrency import run_in_threadpool

from . import auth, db, game_oauth

router = APIRouter()
logger = logging.getLogger(__name__)
STEAM_ENDPOINT = "https://steamcommunity.com/openid/login"
OPENID = "http://specs.openid.net/auth/2.0"
SIGNED_FIELDS = {"op_endpoint", "claimed_id", "identity", "return_to", "response_nonce", "assoc_handle"}


def _availability():
    return {"steam": True, **game_oauth.providers()}


@router.get("/api/accounts/providers")
def providers(user=Depends(auth.require_user)):
    origin_ok = auth.valid_public_origin()
    return [
        {
            "platform": platform,
            "available": bool(origin_ok and available),
            "library_import_available": bool(platform == "steam" and os.getenv("STEAM_API_KEY")),
        }
        for platform, available in _availability().items()
    ]


def callback_url(platform):
    return f"{auth.PUBLIC_BASE_URL}/auth/game/{platform}/callback"


def _steam_return_to(state):
    return callback_url("steam") + "?" + urlencode({"state": state})


def _steam_url(state):
    return STEAM_ENDPOINT + "?" + urlencode({
        "openid.ns": OPENID, "openid.mode": "checkid_setup",
        "openid.return_to": _steam_return_to(state), "openid.realm": auth.PUBLIC_BASE_URL + "/",
        "openid.claimed_id": OPENID + "/identifier_select",
        "openid.identity": OPENID + "/identifier_select",
    })


@router.post("/api/accounts/{platform}/connect")
async def connect(platform: str, request: Request, user=Depends(auth.require_user)):
    available = _availability()
    if platform not in available:
        raise HTTPException(404, "Unknown platform.")
    if not available[platform] or not auth.valid_public_origin():
        raise HTTPException(503, "Profile connection unavailable.")
    session = request.cookies[auth.SESSION_COOKIE]
    state = await run_in_threadpool(db.create_link_flow, session, platform)
    if not state:
        raise HTTPException(401, "Sign in again.")
    try:
        url = _steam_url(state) if platform == "steam" else await game_oauth.start(
            request, platform, state, callback_url(platform)
        )
    except Exception as error:
        logger.warning("Game provider start failed (%s)", type(error).__name__)
        raise HTTPException(503, "Profile connection unavailable.") from None
    return {"url": url}


async def _steam_confirm(params):
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(STEAM_ENDPOINT, data={**params, "openid.mode": "check_authentication"})
        response.raise_for_status()
    return "is_valid:true" in response.text.splitlines()


async def verify_steam(request, state):
    fields = {k: v for k, v in request.query_params.items() if k.startswith("openid.")}
    claimed = fields.get("openid.claimed_id", "")
    subject = re.fullmatch(r"https?://steamcommunity\.com/openid/id/([0-9]{17})", claimed)
    signed = set(fields.get("openid.signed", "").split(","))
    if not (
        fields.get("openid.ns") == OPENID and fields.get("openid.mode") == "id_res"
        and fields.get("openid.op_endpoint") == STEAM_ENDPOINT and subject
        and fields.get("openid.identity") == claimed and fields.get("openid.return_to") == _steam_return_to(state)
        and SIGNED_FIELDS <= signed and fields.get("openid.sig") and fields.get("openid.assoc_handle")
    ):
        raise ValueError("Invalid Steam assertion")
    nonce = fields.get("openid.response_nonce", "")
    issued = datetime.strptime(nonce[:20], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    if abs((datetime.now(timezone.utc) - issued).total_seconds()) > 600:
        raise ValueError("Expired Steam assertion")
    # The signed return_to contains the one-use database state, binding this assertion to this session.
    if not await _steam_confirm(fields):
        raise ValueError("Steam declined the assertion")
    return subject[1], subject[1]


@router.get("/auth/game/{platform}/callback", include_in_schema=False)
async def callback(platform: str, request: Request):
    result = "failed"
    session = request.cookies.get(auth.SESSION_COOKIE)
    state = request.query_params.get("state", "")
    if (
        session and platform in _availability() and re.fullmatch(r"[A-Za-z0-9_-]{43}", state)
        and len(request.query_params) == len(request.query_params.multi_items())
        and await run_in_threadpool(db.consume_link_flow, session, platform, state)
    ):
        try:
            if platform == "steam":
                subject, name = await verify_steam(request, state)
            else:
                subject, name = await game_oauth.verify(request, platform)
            if not isinstance(subject, str) or not subject.strip() or len(subject) > 512:
                raise ValueError("Invalid provider identity")
            if await run_in_threadpool(db.save_verified_account, session, platform, subject, name or subject):
                result = "connected"
        except Exception as error:
            logger.info("Game provider verification failed (%s)", type(error).__name__)
    return RedirectResponse(f"/?account_result={result}#profiles", status_code=303)
