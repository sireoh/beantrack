"""The once-a-day B2 backup: scheduling, upload, and pruning old daily snapshots."""

from datetime import UTC, datetime, time
from zoneinfo import ZoneInfo

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.services import daily_backup
from app.services.backups import BACKUP_PREFIX
from testing.fakes import FakeUpstream


UTC_ZONE = ZoneInfo("UTC")
# New York, not Vancouver: BC is moving to permanent daylight time, so its offsets
# depend on the installed tzdata version.
NEW_YORK = ZoneInfo("America/New_York")


def test_next_run_later_today() -> None:
    now = datetime(2026, 11, 14, 1, 30, tzinfo=UTC)
    at = daily_backup.next_run(now, time(3, 0), UTC_ZONE)
    assert at == datetime(2026, 11, 14, 3, 0, tzinfo=UTC)


def test_next_run_tomorrow_when_time_has_passed_or_is_now() -> None:
    at = time(3, 0)
    tomorrow = datetime(2026, 11, 15, 3, 0, tzinfo=UTC)
    assert daily_backup.next_run(datetime(2026, 11, 14, 3, 0, tzinfo=UTC), at, UTC_ZONE) == tomorrow
    assert daily_backup.next_run(datetime(2026, 11, 14, 23, 59, tzinfo=UTC), at, UTC_ZONE) == tomorrow


def test_next_run_uses_the_configured_time_zone() -> None:
    # 2026-11-14 06:00 UTC is 01:00 in New York (EST, UTC-5): 03:00 local is 08:00 UTC.
    now = datetime(2026, 11, 14, 6, 0, tzinfo=UTC)
    assert daily_backup.next_run(now, time(3, 0), NEW_YORK) == datetime(
        2026, 11, 14, 8, 0, tzinfo=UTC
    )


def test_next_run_keeps_local_time_across_daylight_saving() -> None:
    # Summer (EDT, UTC-4): 03:00 local is 07:00 UTC.
    summer = datetime(2026, 7, 1, 0, 0, tzinfo=UTC)
    assert daily_backup.next_run(summer, time(3, 0), NEW_YORK) == datetime(
        2026, 7, 1, 7, 0, tzinfo=UTC
    )
    # The night DST ends (2026-11-01), the next 03:00 local is already EST: 08:00 UTC.
    before_switch = datetime(2026, 11, 1, 4, 0, tzinfo=UTC)  # 00:00 EDT
    assert daily_backup.next_run(before_switch, time(3, 0), NEW_YORK) == datetime(
        2026, 11, 1, 8, 0, tzinfo=UTC
    )


def test_unknown_time_zone_is_rejected(settings: Settings) -> None:
    with pytest.raises(ValidationError):
        Settings.model_validate(
            {**settings.model_dump(), "daily_backup_timezone": "Mars/Olympus"}
        )


def _http(upstream: FakeUpstream) -> httpx.Client:
    return httpx.Client(transport=upstream.transport())


def test_run_once_uploads_a_daily_snapshot(
    app: FastAPI, client: TestClient, settings: Settings, upstream: FakeUpstream
) -> None:
    daily_backup.run_once(_http(upstream), settings)

    names = list(upstream.b2_files)
    assert len(names) == 1
    assert names[0].startswith(BACKUP_PREFIX) and names[0].endswith("-daily.db.gz")


def test_run_once_keeps_only_the_newest_daily_backups(
    app: FastAPI, admin: TestClient, settings: Settings, upstream: FakeUpstream
) -> None:
    manual = admin.post("/api/admin/backup").json()["name"]
    keep = settings.model_copy(update={"daily_backup_keep": 2})
    http = _http(upstream)

    for _ in range(4):
        daily_backup.run_once(http, keep)

    daily = sorted(n for n in upstream.b2_files if n.endswith("-daily.db.gz"))
    assert len(daily) == 2
    # The two kept are the two most recently uploaded.
    newest = sorted(upstream.b2_files, key=lambda n: upstream.b2_files[n][1])[-2:]
    assert sorted(newest) == daily
    assert manual in upstream.b2_files  # manual backups are never pruned


def test_scheduler_does_not_start_without_b2_or_when_disabled(
    settings: Settings, upstream: FakeUpstream
) -> None:
    http = _http(upstream)
    enabled = settings.model_copy(update={"daily_backup_enabled": True})

    assert daily_backup.start_scheduler(http, settings) is None  # disabled in tests
    assert daily_backup.start_scheduler(http, enabled.model_copy(update={"b2_key_id": ""})) is None

    scheduler = daily_backup.start_scheduler(http, enabled)
    assert scheduler is not None
    scheduler.stop()  # wakes the sleeping thread and joins it
    assert upstream.b2_files == {}
