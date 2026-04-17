import os


DEFAULT_UI_BASE_URL = "https://cerulean-praline-8e5aa6.netlify.app"


def get_ui_base_url() -> str:
    base_url = os.getenv("UI_BASE_URL", DEFAULT_UI_BASE_URL).rstrip("/")
    if not base_url.startswith(("http://", "https://")):
        raise ValueError(f"Некорректный UI_BASE_URL: {base_url}")
    return base_url
