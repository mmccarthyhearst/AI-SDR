"""ICP (Ideal Customer Profile) model."""

import uuid

from sqlalchemy import Boolean, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ai_sdr.db.base import Base
from ai_sdr.db.mixins import TimestampMixin


class ICP(TimestampMixin, Base):
    __tablename__ = "icps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # ICP criteria
    target_industries: Mapped[list | None] = mapped_column(JSON)
    min_employee_count: Mapped[int | None] = mapped_column(Integer)
    max_employee_count: Mapped[int | None] = mapped_column(Integer)
    min_revenue: Mapped[str | None] = mapped_column(String(100))
    max_revenue: Mapped[str | None] = mapped_column(String(100))
    target_titles: Mapped[list | None] = mapped_column(JSON)  # ["VP of Sales", "CRO", ...]
    target_seniority: Mapped[list | None] = mapped_column(JSON)  # ["C-Suite", "VP", ...]
    target_geography: Mapped[list | None] = mapped_column(JSON)  # ["US", "EMEA", ...]
    required_tech_stack: Mapped[list | None] = mapped_column(JSON)

    # Scoring weights (0-100 per criterion)
    scoring_weights: Mapped[dict | None] = mapped_column(JSON)

    # Additional criteria as flexible JSON
    custom_criteria: Mapped[dict | None] = mapped_column(JSON)

    # Franchise-specific criteria
    target_franchise_brands: Mapped[list | None] = mapped_column(JSON)
    min_franchise_count: Mapped[int | None] = mapped_column(Integer)
    max_franchise_count: Mapped[int | None] = mapped_column(Integer)
    is_franchisor_target: Mapped[bool] = mapped_column(Boolean, default=False)
    is_franchisee_target: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<ICP {self.name} active={self.is_active}>"
