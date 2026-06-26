"""Routing service — custom rules engine for lead triage."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_sdr.models.routing_rule import RoutingRule
from ai_sdr.schemas.routing_rule import RoutingRuleCreate, RoutingRuleUpdate


async def create_routing_rule(session: AsyncSession, data: RoutingRuleCreate) -> RoutingRule:
    rule = RoutingRule(
        name=data.name,
        description=data.description,
        priority=data.priority,
        conditions=[c.model_dump() for c in data.conditions],
        action=data.action.model_dump(),
    )
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return rule


async def list_routing_rules(
    session: AsyncSession, active_only: bool = True
) -> list[RoutingRule]:
    query = select(RoutingRule)
    if active_only:
        query = query.where(RoutingRule.is_active == True)  # noqa: E712
    query = query.order_by(RoutingRule.priority.asc())
    result = await session.execute(query)
    return list(result.scalars().all())


async def update_routing_rule(
    session: AsyncSession, rule_id: uuid.UUID, data: RoutingRuleUpdate
) -> RoutingRule | None:
    rule = await session.get(RoutingRule, rule_id)
    if not rule:
        return None
    update_data = data.model_dump(exclude_unset=True)
    if "conditions" in update_data and update_data["conditions"] is not None:
        update_data["conditions"] = [c.model_dump() for c in data.conditions]
    if "action" in update_data and update_data["action"] is not None:
        update_data["action"] = data.action.model_dump()
    for field, value in update_data.items():
        setattr(rule, field, value)
    await session.commit()
    await session.refresh(rule)
    return rule


def evaluate_condition(condition: dict, lead_data: dict) -> bool:
    """Evaluate a single routing condition against lead data.

    Args:
        condition: {"field": "company.industry", "op": "in", "value": ["fintech"]}
        lead_data: Flattened dict with dot-notation keys matching condition fields.
    """
    field = condition.get("field", "")
    op = condition.get("op", "==")
    expected = condition.get("value")
    actual = lead_data.get(field)

    if actual is None:
        return False

    if op == "==":
        return actual == expected
    elif op == "!=":
        return actual != expected
    elif op == ">=":
        return float(actual) >= float(expected)
    elif op == "<=":
        return float(actual) <= float(expected)
    elif op == ">":
        return float(actual) > float(expected)
    elif op == "<":
        return float(actual) < float(expected)
    elif op == "in":
        if isinstance(expected, list):
            return str(actual).lower() in [str(v).lower() for v in expected]
        return False
    elif op == "not_in":
        if isinstance(expected, list):
            return str(actual).lower() not in [str(v).lower() for v in expected]
        return True
    elif op == "contains":
        return str(expected).lower() in str(actual).lower()

    return False


def route_lead(rules: list[RoutingRule], lead_data: dict) -> dict | None:
    """Evaluate routing rules against lead data, return first matching action.

    Args:
        rules: List of RoutingRule objects, sorted by priority.
        lead_data: Dict with keys like "company.industry", "lead.score", etc.

    Returns:
        The action dict from the first matching rule, or None if no match.
    """
    for rule in rules:
        if not rule.is_active:
            continue

        conditions = rule.conditions or []

        # Empty conditions = catch-all / default rule
        if not conditions:
            return rule.action

        # All conditions must match (AND logic)
        if all(evaluate_condition(c, lead_data) for c in conditions):
            return rule.action

    return None
