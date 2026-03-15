"""Pipeline API routes — trigger and monitor agent runs."""

import uuid

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_sdr.api.v1.deps import get_db
from ai_sdr.config import settings
from ai_sdr.models.agent_run import AgentRun, AgentRunStatus
from ai_sdr.schemas.agent import PipelineRunRequest, PipelineRunResponse
from ai_sdr.services import pipeline_service
from ai_sdr.services.icp_service import get_icp

router = APIRouter()


@router.post("/run", response_model=PipelineRunResponse, status_code=202)
async def trigger_pipeline_run(
    request: PipelineRunRequest,
    db: AsyncSession = Depends(get_db),
):
    """Trigger a new pipeline run. Returns immediately with a run ID."""
    icp_id = None
    if request.icp_id:
        icp_id = uuid.UUID(request.icp_id)
        icp = await get_icp(db, icp_id)
        if not icp:
            raise HTTPException(status_code=404, detail="ICP not found")

    run = await pipeline_service.create_pipeline_run(
        db, icp_id=icp_id, trigger="api"
    )

    redis = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    await redis.enqueue_job(
        "run_pipeline",
        str(run.id),
        str(icp_id) if icp_id else None,
        getattr(request, "max_leads", 10),
    )
    await redis.aclose()

    return PipelineRunResponse(
        run_id=str(run.id),
        status=run.status.value,
        message="Pipeline run enqueued for background execution.",
    )


@router.get("/runs")
async def list_pipeline_runs(
    status: AgentRunStatus | None = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    query = select(AgentRun)
    if status:
        query = query.where(AgentRun.status == status)
    query = query.order_by(AgentRun.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    runs = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "status": r.status.value,
            "trigger": r.trigger,
            "leads_sourced": r.leads_sourced,
            "leads_qualified": r.leads_qualified,
            "leads_routed": r.leads_routed,
            "appointments_set": r.appointments_set,
            "error_message": r.error_message,
            "started_at": r.started_at,
            "completed_at": r.completed_at,
            "created_at": r.created_at,
        }
        for r in runs
    ]


@router.get("/runs/{run_id}")
async def get_pipeline_run(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    run = await db.get(AgentRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    return {
        "id": str(run.id),
        "status": run.status.value,
        "trigger": run.trigger,
        "icp_id": str(run.icp_id) if run.icp_id else None,
        "leads_sourced": run.leads_sourced,
        "leads_qualified": run.leads_qualified,
        "leads_routed": run.leads_routed,
        "appointments_set": run.appointments_set,
        "error_message": run.error_message,
        "started_at": run.started_at,
        "completed_at": run.completed_at,
        "created_at": run.created_at,
    }
