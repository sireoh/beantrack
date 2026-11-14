"""Once-a-day backup to Backblaze B2, run on a background thread inside the API process.

One snapshot a day costs about 2 B2 Class C calls (b2_authorize_account +
b2_list_file_names), far under the free 2,500 per day; the upload and the deletes are
Class A, which is free.

Runs only in one process: start uvicorn with a single worker (the default).
"""

import logging
import threading
from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo

import httpx

from app.clients.b2 import B2Client
from app.core.config import Settings
from app.services import backups

# A child of uvicorn's logger, so these INFO lines show up in `docker compose logs`.
log = logging.getLogger("uvicorn.error.daily_backup")


def next_run(now: datetime, at: time, zone: ZoneInfo) -> datetime:
    """The next moment (in UTC) that is time-of-day `at` in `zone`, strictly after `now`.

    Built from the local calendar date each time, so it stays at the same wall-clock time
    across daylight-saving changes.
    """
    local_now = now.astimezone(zone)
    day = local_now.date()
    while True:
        candidate = datetime.combine(day, at, tzinfo=zone).astimezone(UTC)
        if candidate > now:
            return candidate
        day += timedelta(days=1)


def run_once(http: httpx.Client, settings: Settings) -> None:
    """Upload one daily snapshot, then delete daily snapshots beyond the keep count."""
    b2 = B2Client.from_settings(http, settings)
    file = backups.create_backup(b2, settings.database_path, label=backups.DAILY_LABEL)
    log.info("daily backup uploaded: %s (%d bytes)", file.name, file.size)
    for stale in backups.prune_daily_backups(b2, settings.daily_backup_keep):
        log.info("deleted old daily backup: %s", stale.name)


class DailyBackupScheduler:
    def __init__(self, http: httpx.Client, settings: Settings) -> None:
        self._http = http
        self._settings = settings
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, name="daily-backup", daemon=True)

    def start(self) -> None:
        log.info(
            "daily backup scheduled at %s %s, keeping %d",
            self._settings.daily_backup_time.strftime("%H:%M"),
            self._settings.daily_backup_timezone,
            self._settings.daily_backup_keep,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread.is_alive():
            self._thread.join(timeout=5)

    def _loop(self) -> None:
        while True:
            now = datetime.now(UTC)
            at = next_run(now, self._settings.daily_backup_time, self._settings.daily_backup_zone)
            wait = (at - now).total_seconds()
            if self._stop.wait(wait):
                return
            try:
                run_once(self._http, self._settings)
            except Exception:  # keep the schedule alive; try again tomorrow
                log.exception("daily backup failed")


def start_scheduler(http: httpx.Client, settings: Settings) -> DailyBackupScheduler | None:
    """Start the daily backup thread if it is enabled and B2 is configured."""
    if not settings.daily_backup_enabled:
        return None
    if not settings.b2_configured:
        log.info("daily backup disabled: B2 is not configured")
        return None
    scheduler = DailyBackupScheduler(http, settings)
    scheduler.start()
    return scheduler
