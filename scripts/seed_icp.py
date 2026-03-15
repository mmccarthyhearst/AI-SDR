#!/usr/bin/env python3
"""Seed the database with franchise-focused ICP definitions and routing rules.

Usage:
    docker compose up -d postgres
    alembic upgrade head
    python scripts/seed_icp.py
"""

import asyncio
import uuid

from sqlalchemy import text

from ai_sdr.db.session import async_session_factory


async def seed():
    async with async_session_factory() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM icps"))
        count = result.scalar()
        if count and count > 0:
            print(f"Database already has {count} ICP(s). Skipping seed.")
            return

        # ── ICP 1: Franchise Brands (50+ Locations) ──────────────────────────
        icp1_id = str(uuid.uuid4())
        await session.execute(
            text("""
                INSERT INTO icps (
                    id, name, description, is_active,
                    target_industries, min_employee_count, max_employee_count,
                    target_titles, target_seniority, target_geography,
                    scoring_weights, custom_criteria,
                    is_franchisor_target, is_franchisee_target,
                    created_at, updated_at
                ) VALUES (
                    :id, :name, :desc, true,
                    :industries, 50, 10000,
                    :titles, :seniority, :geo,
                    :weights, :criteria,
                    true, false,
                    now(), now()
                )
            """),
            {
                "id": icp1_id,
                "name": "Franchise Brands (50+ Locations)",
                "desc": "Established franchisors with 50+ units seeking operational tech",
                "industries": '["Food & Beverage", "Retail", "Fitness", "Health & Wellness", "Home Services"]',
                "titles": '["VP of Operations", "Director of Franchise Development", "COO", "CEO", "VP of Franchise Development"]',
                "seniority": '["C-Suite", "VP", "Director"]',
                "geo": '["US", "Canada"]',
                "weights": '{"industry": 20, "franchise_count": 30, "seniority": 20, "title": 20, "geography": 10}',
                "criteria": '{"is_franchisor_target": true, "min_franchise_count": 50}',
            },
        )
        print("Created ICP: Franchise Brands (50+ Locations)")

        # ── ICP 2: Multi-Unit Franchisees (5+ Units) ─────────────────────────
        icp2_id = str(uuid.uuid4())
        await session.execute(
            text("""
                INSERT INTO icps (
                    id, name, description, is_active,
                    target_industries, min_employee_count, max_employee_count,
                    target_titles, target_seniority, target_geography,
                    scoring_weights, custom_criteria,
                    is_franchisor_target, is_franchisee_target,
                    created_at, updated_at
                ) VALUES (
                    :id, :name, :desc, true,
                    :industries, 10, 1000,
                    :titles, :seniority, :geo,
                    :weights, :criteria,
                    false, true,
                    now(), now()
                )
            """),
            {
                "id": icp2_id,
                "name": "Multi-Unit Franchisees (5+ Units)",
                "desc": "Multi-unit franchise operators running 5+ locations",
                "industries": '["Food & Beverage", "Retail", "Fitness", "Health & Wellness", "Home Services"]',
                "titles": '["Owner", "Operator", "Director of Operations", "VP of Operations", "President"]',
                "seniority": '["C-Suite", "VP", "Director", "Owner"]',
                "geo": '["US", "Canada"]',
                "weights": '{"industry": 20, "franchise_count": 30, "seniority": 15, "title": 20, "geography": 15}',
                "criteria": '{"is_franchisee_target": true, "min_franchise_count": 5}',
            },
        )
        print("Created ICP: Multi-Unit Franchisees (5+ Units)")

        # ── Routing Rules ────────────────────────────────────────────────────
        await session.execute(
            text("""
                INSERT INTO routing_rules (id, name, description, priority, is_active,
                    conditions, action, created_at, updated_at)
                VALUES
                (
                    gen_random_uuid(),
                    'Franchisor (50+ units)',
                    'Route large franchisors to enterprise franchise team',
                    0, true,
                    '[{"field": "company.franchise_count", "op": ">=", "value": 50}]'::jsonb,
                    '{"team": "enterprise", "rep_name": "Enterprise Franchise Team"}'::jsonb,
                    now(), now()
                ),
                (
                    gen_random_uuid(),
                    'Multi-Unit Franchisee (5+ units)',
                    'Route multi-unit operators to expansion team',
                    10, true,
                    '[{"field": "company.franchise_count", "op": ">=", "value": 5}]'::jsonb,
                    '{"team": "expansion", "rep_name": "Franchise Expansion Team"}'::jsonb,
                    now(), now()
                ),
                (
                    gen_random_uuid(),
                    'Hot Leads (score >= 80)',
                    'Route hot franchise leads to priority team',
                    20, true,
                    '[{"field": "lead.score", "op": ">=", "value": 80}]'::jsonb,
                    '{"team": "priority", "rep_name": "Priority Franchise Team"}'::jsonb,
                    now(), now()
                ),
                (
                    gen_random_uuid(),
                    'Default / Catch-all',
                    'Default routing for unmatched franchise leads',
                    99, true,
                    '[]'::jsonb,
                    '{"team": "general", "rep_name": "General Franchise Sales"}'::jsonb,
                    now(), now()
                )
            """)
        )
        print("Created 4 franchise routing rules")

        # ── Sample Franchise Companies ───────────────────────────────────────
        ot_id = str(uuid.uuid4())
        fg_id = str(uuid.uuid4())
        mu_id = str(uuid.uuid4())

        await session.execute(
            text("""
                INSERT INTO companies (id, name, domain, industry, is_franchisor,
                    franchise_brand, franchise_count, hq_location, source,
                    created_at, updated_at)
                VALUES
                (
                    :id1, 'Orangetheory Fitness', 'orangetheory.com', 'Fitness',
                    true, 'Orangetheory Fitness', 1400,
                    'Fort Lauderdale, FL', 'seed', now(), now()
                ),
                (
                    :id2, 'Five Guys', 'fiveguys.com', 'Food & Beverage',
                    true, 'Five Guys', 1700,
                    'Lorton, VA', 'seed', now(), now()
                ),
                (
                    :id3, 'Apex Multi-Unit Partners', 'apexfranchise.com', 'Food & Beverage',
                    false, 'Five Guys', 8,
                    'Austin, TX', 'seed', now(), now()
                )
            """),
            {"id1": ot_id, "id2": fg_id, "id3": mu_id},
        )
        print("Created 3 sample franchise companies")

        await session.commit()
        print("\nSeed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
