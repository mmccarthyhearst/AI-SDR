"""Unit tests for routing_service — evaluate_condition and route_lead.

These are pure unit tests with no DB; RoutingRule objects are constructed
directly (no async session required).
"""
import uuid

import pytest
from unittest.mock import MagicMock

from ai_sdr.services.routing_service import evaluate_condition, route_lead


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_rule(name="Rule", priority=1, conditions=None, action=None, is_active=True):
    """Build a minimal RoutingRule-like object without hitting the DB."""
    rule = MagicMock()
    rule.name = name
    rule.priority = priority
    rule.conditions = conditions if conditions is not None else []
    rule.action = action if action is not None else {"team": "default"}
    rule.is_active = is_active
    return rule


# ---------------------------------------------------------------------------
# evaluate_condition — equality operators
# ---------------------------------------------------------------------------


def test_evaluate_eq_match():
    assert evaluate_condition({"field": "status", "op": "==", "value": "active"}, {"status": "active"})


def test_evaluate_eq_no_match():
    assert not evaluate_condition({"field": "status", "op": "==", "value": "active"}, {"status": "inactive"})


def test_evaluate_neq_match():
    assert evaluate_condition({"field": "status", "op": "!=", "value": "active"}, {"status": "inactive"})


def test_evaluate_neq_no_match():
    assert not evaluate_condition({"field": "status", "op": "!=", "value": "active"}, {"status": "active"})


# ---------------------------------------------------------------------------
# evaluate_condition — numeric comparisons
# ---------------------------------------------------------------------------


def test_evaluate_gte_match():
    assert evaluate_condition({"field": "score", "op": ">=", "value": 80}, {"score": 85})


def test_evaluate_gte_equal():
    assert evaluate_condition({"field": "score", "op": ">=", "value": 80}, {"score": 80})


def test_evaluate_gte_no_match():
    assert not evaluate_condition({"field": "score", "op": ">=", "value": 80}, {"score": 79})


def test_evaluate_lte_match():
    assert evaluate_condition({"field": "score", "op": "<=", "value": 50}, {"score": 30})


def test_evaluate_gt_match():
    assert evaluate_condition({"field": "score", "op": ">", "value": 80}, {"score": 81})


def test_evaluate_gt_no_match_equal():
    assert not evaluate_condition({"field": "score", "op": ">", "value": 80}, {"score": 80})


def test_evaluate_lt_match():
    assert evaluate_condition({"field": "score", "op": "<", "value": 50}, {"score": 49})


def test_evaluate_lt_no_match_equal():
    assert not evaluate_condition({"field": "score", "op": "<", "value": 50}, {"score": 50})


# ---------------------------------------------------------------------------
# evaluate_condition — list operators
# ---------------------------------------------------------------------------


def test_evaluate_in_match():
    assert evaluate_condition(
        {"field": "industry", "op": "in", "value": ["Fitness", "Food"]},
        {"industry": "fitness"},
    )


def test_evaluate_in_case_insensitive():
    assert evaluate_condition(
        {"field": "industry", "op": "in", "value": ["TECH", "SaaS"]},
        {"industry": "tech"},
    )


def test_evaluate_in_no_match():
    assert not evaluate_condition(
        {"field": "industry", "op": "in", "value": ["Fitness"]},
        {"industry": "Healthcare"},
    )


def test_evaluate_in_non_list_value():
    # "in" with a non-list expected returns False
    assert not evaluate_condition(
        {"field": "industry", "op": "in", "value": "Fitness"},
        {"industry": "Fitness"},
    )


def test_evaluate_not_in_match():
    assert evaluate_condition(
        {"field": "industry", "op": "not_in", "value": ["Fitness", "Food"]},
        {"industry": "healthcare"},
    )


def test_evaluate_not_in_no_match():
    assert not evaluate_condition(
        {"field": "industry", "op": "not_in", "value": ["Fitness", "Food"]},
        {"industry": "fitness"},
    )


# ---------------------------------------------------------------------------
# evaluate_condition — contains operator
# ---------------------------------------------------------------------------


def test_evaluate_contains_match():
    assert evaluate_condition(
        {"field": "company_name", "op": "contains", "value": "Acme"},
        {"company_name": "Acme Franchise Group"},
    )


def test_evaluate_contains_case_insensitive():
    assert evaluate_condition(
        {"field": "company_name", "op": "contains", "value": "acme"},
        {"company_name": "ACME Corp"},
    )


def test_evaluate_contains_no_match():
    assert not evaluate_condition(
        {"field": "company_name", "op": "contains", "value": "Subway"},
        {"company_name": "Acme Corp"},
    )


# ---------------------------------------------------------------------------
# evaluate_condition — edge cases
# ---------------------------------------------------------------------------


def test_evaluate_missing_field_returns_false():
    assert not evaluate_condition({"field": "missing", "op": "==", "value": "x"}, {})


def test_evaluate_unknown_op_returns_false():
    assert not evaluate_condition({"field": "score", "op": "???", "value": 80}, {"score": 80})


# ---------------------------------------------------------------------------
# route_lead — routing logic
# ---------------------------------------------------------------------------


def test_route_lead_first_match_wins():
    rules = [
        _make_rule("High Score", 1, [{"field": "score", "op": ">=", "value": 80}], {"team": "priority"}),
        _make_rule("Default", 99, [], {"team": "default"}),
    ]
    result = route_lead(rules, {"score": 90})
    assert result["team"] == "priority"


def test_route_lead_falls_through_to_catch_all():
    rules = [
        _make_rule("High Score", 1, [{"field": "score", "op": ">=", "value": 90}], {"team": "hot"}),
        _make_rule("Default", 99, [], {"team": "default"}),
    ]
    result = route_lead(rules, {"score": 50})
    assert result["team"] == "default"


def test_route_lead_catch_all_empty_conditions():
    rules = [_make_rule("Default", 99, [], {"team": "default"})]
    result = route_lead(rules, {"score": 10})
    assert result["team"] == "default"


def test_route_lead_no_match_returns_none():
    rules = [
        _make_rule("Hot Only", 1, [{"field": "score", "op": ">=", "value": 90}], {"team": "hot"}),
    ]
    result = route_lead(rules, {"score": 50})
    assert result is None


def test_route_lead_skips_inactive_rules():
    rules = [
        _make_rule("Inactive", 1, [], {"team": "inactive"}, is_active=False),
        _make_rule("Active", 2, [], {"team": "active"}, is_active=True),
    ]
    result = route_lead(rules, {})
    assert result["team"] == "active"


def test_route_lead_all_inactive_returns_none():
    rules = [
        _make_rule("Inactive", 1, [], {"team": "inactive"}, is_active=False),
    ]
    result = route_lead(rules, {})
    assert result is None


def test_route_lead_multiple_conditions_all_must_match():
    rules = [
        _make_rule(
            "Multi-condition",
            1,
            [
                {"field": "score", "op": ">=", "value": 80},
                {"field": "industry", "op": "in", "value": ["Fitness"]},
            ],
            {"team": "fitness-hot"},
        ),
        _make_rule("Default", 99, [], {"team": "default"}),
    ]
    # Both conditions match
    result = route_lead(rules, {"score": 85, "industry": "fitness"})
    assert result["team"] == "fitness-hot"


def test_route_lead_partial_conditions_falls_through():
    rules = [
        _make_rule(
            "Multi-condition",
            1,
            [
                {"field": "score", "op": ">=", "value": 80},
                {"field": "industry", "op": "in", "value": ["Fitness"]},
            ],
            {"team": "fitness-hot"},
        ),
        _make_rule("Default", 99, [], {"team": "default"}),
    ]
    # Score matches but industry doesn't — falls through to default
    result = route_lead(rules, {"score": 85, "industry": "healthcare"})
    assert result["team"] == "default"


def test_route_lead_empty_rules_returns_none():
    result = route_lead([], {"score": 90})
    assert result is None
