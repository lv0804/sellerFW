import os


DEFAULT_BASE_URL = "https://qa-internship.avito.com"


def get_base_url() -> str:
    return os.getenv("BASE_URL", DEFAULT_BASE_URL).rstrip("/")
