# Import and load  .env variables
from dotenv import load_dotenv 
import os ; load_dotenv()
# 
import jwt
from dataclasses import dataclass
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from jwt.exceptions import PyJWTError


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    id: str
    email: str | None = None


_jwks_client: PyJWKClient | None = None


def get_supabase_url() -> str:
    supabase_url = os.getenv("SUPABASE_URL")

    if not supabase_url:
        raise RuntimeError("SUPABASE_URL is not set. Add it to your .env file.")

    return supabase_url.rstrip("/")


def get_jwks_client() -> PyJWKClient:
    global _jwks_client

    if _jwks_client is None:
        jwks_url = f"{get_supabase_url()}/auth/v1/.well-known/jwks.json"
        _jwks_client = PyJWKClient(
            jwks_url,
            cache_jwk_set=True,
            lifespan=300,
        )

    return _jwks_client


def unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Invalid or missing authentication token.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized()

    token = credentials.credentials

    try:
        signing_key = get_jwks_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=[
                "RS256",
                "RS384",
                "RS512",
                "ES256",
                "ES384",
                "ES512",
                "EdDSA",
            ],
            audience=os.getenv("SUPABASE_JWT_AUDIENCE", "authenticated"),
            issuer=f"{get_supabase_url()}/auth/v1",
        )
    except PyJWTError:
        raise unauthorized()

    user_id = payload.get("sub")

    if not user_id:
        raise unauthorized()

    return CurrentUser(
        id=user_id,
        email=payload.get("email"),
    )
