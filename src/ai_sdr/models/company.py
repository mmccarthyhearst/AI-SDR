"""Company model - organizations being prospected."""

import uuid

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_sdr.db.base import Base
from ai_sdr.db.mixins import TimestampMixin


class Company(TimestampMixin, Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    industry: Mapped[str | None] = mapped_column(String(255))
    employee_count_range: Mapped[str | None] = mapped_column(String(50))
    estimated_revenue: Mapped[str | None] = mapped_column(String(100))
    hq_location: Mapped[str | None] = mapped_column(String(255))
    tech_stack: Mapped[dict | None] = mapped_column(JSON)
    funding_stage: Mapped[str | None] = mapped_column(String(100))
    last_funding_amount: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)

    # Franchise-specific fields
    is_franchisor: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    franchise_brand: Mapped[str | None] = mapped_column(String(255), index=True)
    franchise_count: Mapped[int | None] = mapped_column(Integer)
    franchise_fee_range: Mapped[str | None] = mapped_column(String(100))
    franchise_territories: Mapped[list | None] = mapped_column(JSON)
    franchise_network_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id")
    )

    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    crm_id: Mapped[str | None] = mapped_column(String(255), index=True)
    source: Mapped[str] = mapped_column(String(100), default="web_scrape")
    raw_data: Mapped[dict | None] = mapped_column(JSON)

    # Relationships
    contacts: Mapped[list["Contact"]] = relationship(back_populates="company")  # noqa: F821
    leads: Mapped[list["Lead"]] = relationship(back_populates="company", foreign_keys="[Lead.company_id]")  # noqa: F821
    franchise_network: Mapped["Company | None"] = relationship(
        "Company",
        remote_side="Company.id",
        foreign_keys="[Company.franchise_network_id]",
    )

    def __repr__(self) -> str:
        return f"<Company {self.name} ({self.domain})>"
