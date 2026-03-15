"""Background tasks for pipeline execution via ARQ."""

import json
import logging
import uuid

logger = logging.getLogger(__name__)


async def run_pipeline(ctx: dict, run_id: str, icp_id: str | None = None, max_leads: int = 10) -> dict:
    """Execute the full SDR pipeline asynchronously.

    Args:
        ctx: ARQ context dict (contains 'redis' ArqRedis connection)
        run_id: UUID string of the AgentRun record
        icp_id: Optional ICP UUID string. Uses first active ICP if None.
        max_leads: Maximum leads to source in this run.

    Returns:
        Dict with run_id, status, result/error.
    """
    from ai_sdr.db.session import async_session_factory
    from ai_sdr.services.icp_service import get_icp, list_icps

    run_uuid = uuid.UUID(run_id)
    logger.info(f"Starting pipeline run {run_id}")

    try:
        async with async_session_factory() as session:
            if icp_id:
                icp = await get_icp(session, uuid.UUID(icp_id))
            else:
                icps = await list_icps(session)
                icp = icps[0] if icps else None

            if not icp:
                return {"run_id": run_id, "status": "failed", "error": "No active ICP found"}

            from ai_sdr.services.pipeline_service import prepare_crew_inputs
            crew_inputs = await prepare_crew_inputs(session, icp, max_leads=max_leads)

        from ai_sdr.agents.crew import create_sdr_crew
        from ai_sdr.services.pipeline_service import (
            complete_pipeline_run,
            fail_pipeline_run,
            start_pipeline_run,
        )

        async with async_session_factory() as session:
            await start_pipeline_run(session, run_uuid)

        crew = create_sdr_crew(
            icp_criteria=crew_inputs["icp_criteria"],
            scoring_weights=crew_inputs.get("scoring_weights", "{}"),
            routing_rules=crew_inputs.get("routing_rules", "[]"),
            max_leads=crew_inputs.get("max_leads", max_leads),
        )
        result = crew.kickoff()

        async with async_session_factory() as session:
            await complete_pipeline_run(session, run_uuid)

        logger.info(f"Pipeline run {run_id} completed")
        return {"run_id": run_id, "status": "completed", "result": str(result)}
    except Exception as e:
        logger.error(f"Pipeline run {run_id} failed: {e}")
        try:
            from ai_sdr.db.session import async_session_factory
            from ai_sdr.services.pipeline_service import fail_pipeline_run

            async with async_session_factory() as session:
                await fail_pipeline_run(session, run_uuid, str(e))
        except Exception:
            pass
        return {"run_id": run_id, "status": "failed", "error": str(e)}


async def schedule_follow_up(ctx: dict, lead_id: str, template_name: str, delay_hours: int = 72) -> dict:
    """Queue a follow-up email for a lead after a delay.

    Args:
        ctx: ARQ context dict
        lead_id: UUID string of the Lead record
        template_name: Email template key (e.g. 'follow_up_1', 'follow_up_2')
        delay_hours: Hours delay (informational only — ARQ handles actual defer timing)

    Returns:
        Dict with status and result.
    """
    from ai_sdr.db.session import async_session_factory
    from ai_sdr.services.lead_service import get_lead
    from ai_sdr.tools.email_tool import send_email_with_template

    logger.info(f"Sending follow-up {template_name} for lead {lead_id}")
    try:
        async with async_session_factory() as session:
            lead = await get_lead(session, uuid.UUID(lead_id))

        if not lead:
            return {"status": "failed", "error": f"Lead {lead_id} not found"}

        company_name = lead.company.name if lead.company else ""
        contact_email = lead.contact.email if lead.contact else None
        if not contact_email:
            return {"status": "failed", "error": "Lead has no contact email"}

        variables_json = json.dumps({"company_name": company_name})
        result = send_email_with_template(
            template_name=template_name,
            to_email=contact_email,
            variables=variables_json,
        )
        return {"status": "sent", "result": result}
    except Exception as e:
        logger.error(f"Follow-up for lead {lead_id} failed: {e}")
        return {"status": "failed", "error": str(e)}


async def sync_crm_leads(ctx: dict, batch_size: int = 50) -> dict:
    """Batch sync ROUTED leads to Salesforce CRM.

    Args:
        ctx: ARQ context dict
        batch_size: Max number of leads to sync in one batch.

    Returns:
        Dict with count of synced leads.
    """
    from ai_sdr.db.session import async_session_factory
    from ai_sdr.models.lead import LeadStatus
    from ai_sdr.services.lead_service import list_leads
    from ai_sdr.tools.crm import sync_lead_to_crm

    logger.info(f"Syncing up to {batch_size} leads to CRM")
    synced = 0
    try:
        async with async_session_factory() as session:
            leads = await list_leads(session, status=LeadStatus.ROUTED, limit=batch_size)

        for lead in leads:
            if lead.contact and lead.company:
                sync_lead_to_crm(
                    first_name=lead.contact.first_name,
                    last_name=lead.contact.last_name,
                    email=lead.contact.email,
                    company=lead.company.name,
                    title=lead.contact.title or "",
                    franchise_brand=getattr(lead, "franchise_brand", "") or "",
                    franchise_count=str(lead.company.franchise_count or ""),
                )
                synced += 1
        logger.info(f"Synced {synced} leads to CRM")
        return {"synced": synced}
    except Exception as e:
        logger.error(f"CRM sync failed: {e}")
        return {"synced": synced, "error": str(e)}


async def daily_pipeline_run(ctx: dict) -> dict:
    """Cron job: trigger a pipeline run with the active ICP daily.

    This function is called by the ARQ scheduler. It enqueues a run_pipeline
    job rather than executing directly, so the pipeline is retryable.

    Args:
        ctx: ARQ context dict (contains 'redis' ArqRedis connection)

    Returns:
        Dict with run_id of the enqueued run.
    """
    from ai_sdr.db.session import async_session_factory
    from ai_sdr.services.icp_service import list_icps
    from ai_sdr.services.pipeline_service import create_pipeline_run

    logger.info("Daily pipeline cron triggered")
    try:
        async with async_session_factory() as session:
            icps = await list_icps(session)
            if not icps:
                logger.warning("No active ICP found for daily run")
                return {"error": "No active ICP"}
            run = await create_pipeline_run(session, trigger="cron")

        redis = ctx["redis"]
        await redis.enqueue_job("run_pipeline", str(run.id), str(icps[0].id))
        logger.info(f"Enqueued daily pipeline run {run.id}")
        return {"run_id": str(run.id)}
    except Exception as e:
        logger.error(f"Daily pipeline cron failed: {e}")
        return {"error": str(e)}


async def cleanup_stale_runs(ctx: dict, stale_hours: int = 2) -> dict:
    """Mark pipeline runs stuck in RUNNING state as FAILED.

    Args:
        ctx: ARQ context dict
        stale_hours: Runs older than this many hours in RUNNING state are marked FAILED.

    Returns:
        Dict with count of cleaned-up runs.
    """
    from datetime import datetime, timedelta, timezone

    from sqlalchemy import select

    from ai_sdr.db.session import async_session_factory
    from ai_sdr.models.agent_run import AgentRun, AgentRunStatus
    from ai_sdr.services.pipeline_service import fail_pipeline_run

    cutoff = datetime.now(timezone.utc) - timedelta(hours=stale_hours)
    logger.info(f"Cleaning up stale runs older than {stale_hours}h")

    cleaned = 0
    try:
        async with async_session_factory() as session:
            result = await session.execute(
                select(AgentRun).where(
                    AgentRun.status == AgentRunStatus.RUNNING,
                    AgentRun.started_at < cutoff,
                )
            )
            stale = list(result.scalars().all())
            for run in stale:
                await fail_pipeline_run(session, run.id, "Run timed out (stale cleanup)")
                cleaned += 1
        logger.info(f"Cleaned up {cleaned} stale runs")
        return {"cleaned_up": cleaned}
    except Exception as e:
        logger.error(f"Stale run cleanup failed: {e}")
        return {"cleaned_up": cleaned, "error": str(e)}
