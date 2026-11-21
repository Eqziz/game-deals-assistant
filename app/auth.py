"""Google sign-in and browser session handling."""

import logging
import os
import secrets
from urllib.parse import urlsplit

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from starlette.concurrency import run_in_threadpool
from starlette.middleware.sessions import SessionMiddleware

from . import db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", include_in_schema=False)
SESSION_COOKIE = "gda_session"
SESSION_SECONDS = 30 * 24 * 60 * 60
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")
SESSION_SECRET = os.environ.get("SESSION_SECRET", "")

oauth = OAuth()
google = oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile", "code_challenge_method": "S256"},
)


def _configured():
    try:
        origin = urlsplit(PUBLIC_BASE_URL)
        secure = origin.scheme == "https" or (
            origin.scheme == "http" and origin.hostname in {"localhost", "127.0.0.1", "::1"}
        )
        return bool(
            origin.hostname and secure and not origin.username and not origin.password
            and not origin.path and not origin.query and not origin.fragment
            and google.client_id and google.client_secret and len(SESSION_SECRET) >= 32
        )
    except ValueError:
        return False


def safe_next(value):
    if (value.startswith("/") and not value.startswith("//") and "\\" not in value
            and not any(ord(ch) < 32 or ord(ch) == 127 for ch in value)):
        return value
    return "/"


def optional_user(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    return db.get_session_user(token) if token else None


def require_user(user=Depends(optional_user)):
    if user is None:
        raise HTTPException(401, "Sign in to access this account.")
    return user


class _RedactCallbackQuery(logging.Filter):
    def filter(self, record):
        args = record.args
        if isinstance(args, tuple) and len(args) == 5 and isinstance(args[2], str):
            path = args[2].split("?", 1)[0]
            if path == "/auth/callback":
                record.args = (*args[:2], path, *args[3:])
        return True


def install_auth(app: FastAPI):
    logging.getLogger("uvicorn.access").addFilter(_RedactCallbackQuery())
    # This cookie holds only the short-lived OIDC flow. The login session is in the database.
    app.add_middleware(
        SessionMiddleware, secret_key=SESSION_SECRET or secrets.token_urlsafe(32),
        session_cookie="gda_login", max_age=600, path="/auth",
        same_site="lax", https_only=PUBLIC_BASE_URL.startswith("https://"),
    )

    @app.middleware("http")
    async def browser_security(request, call_next):
        if request.method not in {"GET", "HEAD", "OPTIONS"} and request.cookies.get(SESSION_COOKIE):
            origin = request.headers.get("origin")
            expected = PUBLIC_BASE_URL or str(request.base_url).rstrip("/")
            if origin != expected and (origin is not None or request.headers.get("sec-fetch-site") != "same-origin"):
                return JSONResponse({"detail": "Same-origin request required."}, status_code=403)
        response = await call_next(request)
        if request.url.path.startswith(("/auth/", "/api/")):
            response.headers["Cache-Control"] = "private, no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    app.include_router(router)


@router.get("/login")
async def login(request: Request, next_path: str = Query("/", alias="next", max_length=2048)):
    if not _configured():
        return RedirectResponse("/?auth_error=unavailable", status_code=303)
    request.session.clear()
    request.session["next"] = safe_next(next_path)
    try:
        return await google.authorize_redirect(request, PUBLIC_BASE_URL + "/auth/callback")
    except Exception as error:
        logger.warning("Could not start Google sign-in (%s)", type(error).__name__)
        request.session.clear()
        return RedirectResponse("/?auth_error=unavailable", status_code=303)


@router.get("/callback")
async def callback(request: Request):
    next_path = safe_next(request.session.get("next", "/"))
    if not _configured():
        return RedirectResponse("/?auth_error=unavailable", status_code=303)
    try:
        # Authlib checks state and verifies the ID token signature, issuer, audience and nonce.
        token = await google.authorize_access_token(request)
        claims = token.get("userinfo") or {}
        if not (claims.get("sub") and claims.get("email") and claims.get("email_verified") is True):
            raise ValueError("Missing verified Google identity")
    except Exception as error:
        logger.info("Google sign-in failed (%s)", type(error).__name__)
        return RedirectResponse("/?auth_error=failed", status_code=303)
    finally:
        request.session.clear()

    user = await run_in_threadpool(
        db.get_or_create_google_user, claims["sub"], claims["email"], claims.get("name") or claims["email"]
    )
    previous = request.cookies.get(SESSION_COOKIE)
    if previous:
        await run_in_threadpool(db.delete_session, previous)
    session = await run_in_threadpool(db.create_session, user["id"], SESSION_SECONDS)
    response = RedirectResponse(next_path, status_code=303)
    response.set_cookie(
        SESSION_COOKIE, session, max_age=SESSION_SECONDS, httponly=True,
        secure=PUBLIC_BASE_URL.startswith("https://"), samesite="lax", path="/",
    )
    return response


@router.post("/logout")
def logout(request: Request):
    session = request.cookies.get(SESSION_COOKIE)
    if session:
        db.delete_session(session)
    request.session.clear()
    response = Response(status_code=204)
    response.delete_cookie(
        SESSION_COOKIE, httponly=True, secure=PUBLIC_BASE_URL.startswith("https://"), samesite="lax",
    )
    return response
