"""Routing Rules API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ai_sdr.api.v1.deps import get_db, verify_api_key
from ai_sdr.schemas.routing_rule import RoutingRuleCreate, RoutingRuleResponse, RoutingRuleUpdate
from ai_sdr.services import routing_service

router = APIRouter()


@router.get("", response_model=list[RoutingRuleResponse], dependencies=[Depends(verify_api_key)])
async def list_routing_rules(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    return await routing_service.list_routing_rules(db, active_only=active_only)


@router.get("/{rule_id}", response_model=RoutingRuleResponse, dependencies=[Depends(verify_api_key)])
async def get_routing_rule(rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from ai_sdr.models.routing_rule import RoutingRule

    rule = await db.get(RoutingRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Routing rule not found")
    return rule


@router.post("", response_model=RoutingRuleResponse, status_code=201, dependencies=[Depends(verify_api_key)])
async def create_routing_rule(data: RoutingRuleCreate, db: AsyncSession = Depends(get_db)):
    return await routing_service.create_routing_rule(db, data)


@router.patch("/{rule_id}", response_model=RoutingRuleResponse, dependencies=[Depends(verify_api_key)])
async def update_routing_rule(
    rule_id: uuid.UUID,
    data: RoutingRuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    rule = await routing_service.update_routing_rule(db, rule_id, data)
    if not rule:
        raise HTTPException(status_code=404, detail="Routing rule not found")
    return rule


@router.delete("/{rule_id}", status_code=204, dependencies=[Depends(verify_api_key)])
async def delete_routing_rule(rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from ai_sdr.models.routing_rule import RoutingRule

    rule = await db.get(RoutingRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Routing rule not found")
    rule.is_active = False
    await db.commit()


class RulePriorityItem(BaseModel):
    id: uuid.UUID
    priority: int


@router.post("/reorder", status_code=200, dependencies=[Depends(verify_api_key)])
async def reorder_routing_rules(
    items: list[RulePriorityItem],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Batch-update routing rule priorities. Send list of {id, priority} pairs."""
    from ai_sdr.models.routing_rule import RoutingRule

    updated = 0
    for item in items:
        rule = await db.get(RoutingRule, item.id)
        if rule:
            rule.priority = item.priority
            updated += 1
    await db.commit()
    return {"updated": updated}
