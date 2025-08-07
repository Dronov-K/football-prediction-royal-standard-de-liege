import os
import requests
import logging
from pathlib import Path

from dotenv import dotenv_values, set_key
from config import settings

logger = logging.getLogger(__name__)

# Path to .env
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"
DROPBOX_TOKEN_URL = settings.dropbox_token_url


def refresh_access_token():
    """
    Refresh Dropbox access_token using refresh_token and save it in .env
    """

    refresh_token = settings.dropbox_refresh_token
    app_key = settings.dropbox_app_key
    app_secret = settings.dropbox_app_secret

    if not all([refresh_token, app_key, app_secret]):
        logger.error(f"Dropbox required keys is missing: DROPBOX_REFRESH_TOKEN, APP_KEY or APP_SECRET")
        raise ValueError("Dropbox required keys is missing: DROPBOX_REFRESH_TOKEN, APP_KEY or APP_SECRET")

    response = requests.post(
        DROPBOX_TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": app_key,
            "client_secret": app_secret,
        }
    )

    if response.status_code != 200:
        logger.error(f"Token update error: {response.status_code} — {response.text}")
        raise RuntimeError(f"Token update error: {response.status_code} — {response.text}")

    new_token = response.json()["access_token"]

    try:
        set_key(str(ENV_PATH), "DROPBOX_ACCESS_TOKEN", new_token)
        os.environ["DROPBOX_ACCESS_TOKEN"] = new_token
        settings.dropbox_access_token = new_token
    except Exception as e:
        logger.error(f"Dropbox access token update failed {e}")
        raise

    return new_token
