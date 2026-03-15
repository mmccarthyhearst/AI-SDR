"""ARQ worker configuration."""

from arq.connections import RedisSettings
from arq.cron import cron

from ai_sdr.config import settings
from ai_sdr.workers.tasks import (
    cleanup_stale_runs,
    daily_pipeline_run,
    run_pipeline,
    schedule_follow_up,
    sync_crm_leads,
)


class WorkerSettings:
    """ARQ WorkerSettings — entry point for `python -m arq ai_sdr.workers.settings.WorkerSettings`."""

    functions = [run_pipeline, schedule_follow_up, sync_crm_leads, cleanup_stale_runs]
    cron_jobs = [
        # daily_pipeline_run at 08:00 UTC
        cron(daily_pipeline_run, hour=8, minute=0),
        # cleanup_stale_runs every hour on the hour
        cron(cleanup_stale_runs, minute=0),
    ]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    max_jobs = 10
    job_timeout = 3600  # 1 hour max per job
    keep_result = 86400  # keep results for 24 hours
