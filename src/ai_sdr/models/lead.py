"""Lead model - the core entity tracking a prospect through the pipeline."""

import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_sdr.db.base import Base
from ai_sdr.db.mixins import TimestampMixin


class LeadStatus(str, enum.Enum):
    NEW = "new"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
    ROUTED = "routed"
    CONTACTED = "contacted"
    MEETING_BOOKED = "meeting_booked"
    CONVERTED = "converted"


class LeadTier(str, enum.Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class Lead(TimestampMixin, Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False
    )
    icp_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("icps.id")
    )
    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_runs.id")
    )

    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus), default=LeadStatus.NEW, nullable=False
    )
    score: Mapped[int | None] = mapped_column(Integer)
    tier: Mapped[LeadTier | None] = mapped_column(Enum(LeadTier))
    qualification_reasoning: Mapped[str | None] = mapped_column(Text)
    buying_signals: Mapped[dict | None] = mapped_column(JSON)

    assigned_team: Mapped[str | None] = mapped_column(String(255))
    assigned_rep_id: Mapped[str | None] = mapped_column(String(255))
    assigned_rep_name: Mapped[str | None] = mapped_column(String(255))
    routing_reasoning: Mapped[str | None] = mapped_column(Text)
    disqualification_reason: Mapped[str | None] = mapped_column(Text)

    # Franchise expansion tracking
    franchise_brand: Mapped[str | None] = mapped_column(String(255))
    franchise_network_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id")
    )
    is_network_expansion: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    company: Mapped["Company"] = relationship(back_populates="leads", foreign_keys="[Lead.company_id]")  # noqa: F821
    contact: Mapped["Contact"] = relationship(back_populates="leads")  # noqa: F821
    outreach_messages: Mapped[list["Outreach"]] = relationship(back_populates="lead")  # noqa: F821
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="lead")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Lead {self.id} status={self.status.value}>"
