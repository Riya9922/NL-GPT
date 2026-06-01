import ipaddress
import socket
from urllib.parse import urlparse

import httpx

from app.errors import AppError

BLOCKED_SCHEMES = {"file", "ftp", "gopher"}
FETCH_TIMEOUT = 15.0
MAX_FETCH_BYTES = 512_000


def _is_private_host(host: str) -> bool:
    if host in ("localhost", "127.0.0.1", "::1"):
        return True
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return True
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return True
    return False


def validate_public_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        raise AppError("INVALID_URL", "Only http and https URLs are allowed", 400)
    if not parsed.hostname:
        raise AppError("INVALID_URL", "URL must include a hostname", 400)
    if _is_private_host(parsed.hostname):
        raise AppError("INVALID_URL", "Private or local URLs are not allowed", 400)
    return parsed.geturl()


async def fetch_url_text(url: str) -> str:
    safe_url = validate_public_url(url)
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=FETCH_TIMEOUT,
        headers={"User-Agent": "AI-Output-Evaluation/1.0"},
    ) as client:
        response = await client.get(safe_url)
        response.raise_for_status()
        content = response.text[:MAX_FETCH_BYTES]
    # Minimal HTML strip
    if "<html" in content.lower():
        import re

        content = re.sub(r"<script[^>]*>[\s\S]*?</script>", " ", content, flags=re.I)
        content = re.sub(r"<style[^>]*>[\s\S]*?</style>", " ", content, flags=re.I)
        content = re.sub(r"<[^>]+>", " ", content)
        content = re.sub(r"\s+", " ", content)
    return content.strip()
