from random import choice

import httpx
from loguru import logger

from .consts import ACCEPT, TIMEOUT, USER_AGENT

headers = {
    "user-agent": choice(USER_AGENT),
    "accept": ACCEPT,
    "X-DNS-Prefetch-Control": "off",
}


async def get_request(
    url: str,
    *,
    headers: dict = headers,
    query_params: dict = {},
) -> httpx.Response:
    async with httpx.AsyncClient(
        headers=headers,
        timeout=TIMEOUT,
    ) as client:
        try:
            resp = await client.get(
                url, params=query_params, follow_redirects=True, timeout=20
            )  # noqa E501
            resp = (
                resp
                if resp.status_code == httpx.codes.OK
                else httpx.Response(status_code=resp.status_code)
            )
            logger.info(f"GET {url}, status_code={resp.status_code}")
            return resp
        except Exception as exc:
            logger.warning(f"Check invalid url {url}")
            logger.error(exc)
            return httpx.Response(status_code=httpx.codes.NOT_FOUND)
