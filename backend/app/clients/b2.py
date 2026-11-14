"""Backblaze B2 client (native API v2, https://www.backblaze.com/apidocs).

Uses the same application key as Litestream (B2_KEY_ID / B2_APPLICATION_KEY) but talks
to B2's native API through the shared httpx client, so no AWS SDK is needed and tests
can mock it like every other upstream.
"""

import hashlib
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote

import httpx
from pydantic import BaseModel

from app.core.errors import AppError, NotFoundError, UpstreamError

AUTHORIZE_URL = "https://api.backblazeb2.com/b2api/v2/b2_authorize_account"


class B2File(BaseModel):
    id: str  # B2 fileId (identifies this exact file version)
    name: str
    size: int
    uploaded_at: datetime


class _Auth(BaseModel):
    token: str
    api_url: str
    download_url: str
    account_id: str
    bucket_id: str


class B2Client:
    def __init__(
        self, http: httpx.Client, *, key_id: str, application_key: str, bucket_name: str
    ) -> None:
        self._http = http
        self._key_id = key_id
        self._application_key = application_key
        self._bucket_name = bucket_name
        self._auth: _Auth | None = None

    # --- public API -------------------------------------------------------------

    def upload(self, name: str, data: bytes, content_type: str) -> B2File:
        auth = self._authorize()
        target = self._json(
            "POST",
            f"{auth.api_url}/b2api/v2/b2_get_upload_url",
            auth.token,
            {"bucketId": auth.bucket_id},
        )
        response = self._send(
            "POST",
            str(target["uploadUrl"]),
            content=data,
            headers={
                "Authorization": str(target["authorizationToken"]),
                "X-Bz-File-Name": quote(name, safe="/"),
                "Content-Type": content_type,
                "Content-Length": str(len(data)),
                "X-Bz-Content-Sha1": hashlib.sha1(data).hexdigest(),
            },
        )
        return _to_file(_body(response))

    def list_files(self, prefix: str) -> list[B2File]:
        auth = self._authorize()
        files: list[B2File] = []
        start: str | None = None
        while True:
            body: dict[str, Any] = {"bucketId": auth.bucket_id, "prefix": prefix, "maxFileCount": 1000}
            if start:
                body["startFileName"] = start
            page = self._json("POST", f"{auth.api_url}/b2api/v2/b2_list_file_names", auth.token, body)
            files.extend(_to_file(item) for item in page.get("files", []))
            start = page.get("nextFileName")
            if not start:
                return files

    def delete(self, file: B2File) -> None:
        auth = self._authorize()
        self._json(
            "POST",
            f"{auth.api_url}/b2api/v2/b2_delete_file_version",
            auth.token,
            {"fileName": file.name, "fileId": file.id},
        )

    def download(self, name: str) -> bytes:
        auth = self._authorize()
        url = f"{auth.download_url}/file/{quote(self._bucket_name)}/{quote(name, safe='/')}"
        response = self._send("GET", url, headers={"Authorization": auth.token})
        if response.status_code == 404:
            raise NotFoundError(f"Backup {name} not found")
        _raise_for_status(response)
        return response.content

    # --- internals --------------------------------------------------------------

    def _authorize(self) -> _Auth:
        if self._auth is not None:
            return self._auth
        response = self._send("GET", AUTHORIZE_URL, auth=(self._key_id, self._application_key))
        if response.status_code == 401:
            raise AppError("Backblaze rejected B2_KEY_ID / B2_APPLICATION_KEY")
        data = _body(response)

        token = str(data["authorizationToken"])
        api_url = str(data["apiUrl"])
        allowed = data.get("allowed") or {}
        bucket_id = allowed.get("bucketId")
        if allowed.get("bucketName") not in (None, self._bucket_name):
            raise AppError(f"The B2 key is restricted to another bucket than {self._bucket_name}")
        if not bucket_id:
            buckets = self._json(
                "POST",
                f"{api_url}/b2api/v2/b2_list_buckets",
                token,
                {"accountId": data["accountId"], "bucketName": self._bucket_name},
            ).get("buckets", [])
            if not buckets:
                raise AppError(f"B2 bucket {self._bucket_name} not found")
            bucket_id = buckets[0]["bucketId"]

        self._auth = _Auth(
            token=token,
            api_url=api_url,
            download_url=str(data["downloadUrl"]),
            account_id=str(data["accountId"]),
            bucket_id=str(bucket_id),
        )
        return self._auth

    def _json(self, method: str, url: str, token: str, body: dict[str, Any]) -> dict[str, Any]:
        return _body(self._send(method, url, json=body, headers={"Authorization": token}))

    def _send(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        try:
            return self._http.request(method, url, timeout=120.0, **kwargs)
        except httpx.HTTPError as exc:
            raise UpstreamError("Backblaze B2 is unreachable") from exc


def _raise_for_status(response: httpx.Response) -> None:
    if response.is_error:
        try:
            message = response.json().get("message") or response.text
        except ValueError:
            message = response.text
        raise UpstreamError(f"Backblaze B2 returned HTTP {response.status_code}: {message}")


def _body(response: httpx.Response) -> dict[str, Any]:
    _raise_for_status(response)
    try:
        data = response.json()
    except ValueError as exc:
        raise UpstreamError("Backblaze B2 returned invalid JSON") from exc
    if not isinstance(data, dict):
        raise UpstreamError("Backblaze B2 returned an unexpected response")
    return data


def _to_file(item: dict[str, Any]) -> B2File:
    return B2File(
        id=str(item["fileId"]),
        name=str(item["fileName"]),
        size=int(item.get("contentLength") or 0),
        uploaded_at=datetime.fromtimestamp(int(item["uploadTimestamp"]) / 1000, tz=UTC),
    )
