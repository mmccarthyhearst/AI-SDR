#!/usr/bin/env python3
"""Seed the database with initial ICP definitions and routing rules.

Usage:
    # First, ensure PostgreSQL is running and migrations are applied:
    #   docker compose up -d postgres
    #   alembic upgrade head
    #
    # Then run:
    #   python scripts/seed_icp.py
"""

import asyncio

from sqlalchemy import text

from ai_sdr.db.session import async_session_factory


async def seed():
    async with async_session_factory() as session:
        # Check if data already exists
        result = await session.execute(text("SELECT COUNT(*) FROM icps"))
        count = result.scalar()
        if count and count > 0:
            print(f"Database already has {count} ICP(s). Skipping seed.")
            return

        # ── ICP Definitions ──────────────────────────────────────

        await session.execute(
            text("""
                INSERT INTO icps (id, name, description, is_active,
                    target_industries, min_employee_count, max_employee_count,
                    min_revenue, max_revenue, target_titles, target_seniority,
                    target_geography, required_tech_stack, scoring_weights,
                    created_at, updated_at)
                VALUES (
                    gen_random_uuid(),
                    'Enterprise SaaS',
                    'Mid-to-large SaaS companies with established sales teams',
                    true,
                    '["Technology", "SaaS", "Software", "Cloud Computing"]'::jsonb,
                    100, 5000,
                    '$10M', '$500M',
                    '["VP of Sales", "CRO", "Head of Revenue", "VP of Business Development", "Director of Sales"]'::jsonb,
                    '["C-Suite", "VP", "Director"]'::jsonb,
                    '["US", "Canada", "United Kingdom"]'::jsonb,
                    '["Salesforce", "HubSpot"]'::jsonb,
                    '{"industry": 25, "company_size": 20, "seniority": 20, "title": 15, "geography": 10, "tech_stack": 10}'::jsonb,
                    now(), now()
                )
            """)
        )
        print("Created ICP: Enterprise SaaS")

        await session.execute(
            text("""
                INSERT INTO icps (id, name, description, is_active,
                    target_industries, min_employee_count, max_employee_count,
                    min_revenue, max_revenue, target_titles, target_seniority,
                    target_geography, required_tech_stack, scoring_weights,
                    created_at, updated_at)
                VALUES (
                    gen_random_uuid(),
                    'Growth-Stage Fintech',
                    'Fintech companies in growth phase looking to scale their sales',
                    true,
                    '["Fintech", "Financial Services", "Banking", "Insurance Technology"]'::jsonb,
                    50, 1000,
                    '$5M', '$100M',
                    '["VP of Sales", "Head of Growth", "CRO", "VP of Partnerships"]'::jsonb,
                    '["C-Suite", "VP", "Director"]'::jsonb,
                    '["US", "United Kingdom", "Germany"]'::jsonb,
                    '["Stripe", "Plaid"]'::jsonb,
                    '{"industry": 30, "company_size": 15, "seniority": 20, "title": 15, "geography": 10, "tech_stack": 10}'::jsonb,
                    now(), now()
                )
            """)
        )
        print("Created ICP: Growth-Stage Fintech")

        # ── Routing Rules ────────────────────────────────────────

        await session.execute(
            text("""
                INSERT INTO routing_rules (id, name, description, priority, is_active,
                    conditions, action, created_at, updated_at)
                VALUES
                (
                    gen_random_uuid(),
                    'Enterprise (500+ employees)',
                    'Route large companies to the Enterprise sales team',
                    0, true,
                    '[{"field": "company.employee_count", "op": ">=", "value": 500}]'::jsonb,
                    '{"team": "enterprise", "rep_name": "Enterprise Team"}'::jsonb,
                    now(), now()
                ),
                (
                    gen_random_uuid(),
                    'Fintech Vertical',
                    'Route fintech companies to the Financial Services team',
                    10, true,
                    '[{"field": "company.industry", "op": "in", "value": ["Fintech", "Financial Services", "Banking"]}]'::jsonb,
                    '{"team": "financial_services", "rep_name": "FinServ Team"}'::jsonb,
                    now(), now()
                ),
                (
                    gen_random_uuid(),
                    'Hot Leads',
                    'Route hot leads (score 80+) to the high-value team',
                    20, true,
                    '[{"field": "lead.score", "op": ">=", "value": 80}]'::jsonb,
                    '{"team": "high_value", "rep_name": "High-Value Team"}'::jsonb,
                    now(), now()
                ),
                (
                    gen_random_uuid(),
                    'Default / General',
                    'Catch-all rule for leads that do not match other criteria',
                    99, true,
                    '[]'::jsonb,
                    '{"team": "general", "rep_name": "General Sales Team"}'::jsonb,
                    now(), now()
                )
            """)
        )
        print("Created 4 routing rules: Enterprise, Fintech, Hot Leads, Default")

        await session.commit()
        print("\nSeed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
