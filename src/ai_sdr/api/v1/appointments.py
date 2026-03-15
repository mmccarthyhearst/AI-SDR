"""Appointment API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_sdr.api.v1.deps import get_db, verify_api_key
from ai_sdr.models.appointment import Appointment, AppointmentStatus
from ai_sdr.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate

router = APIRouter()


@router.get("", response_model=list[AppointmentResponse], dependencies=[Depends(verify_api_key)])
async def list_appointments(
    lead_id: uuid.UUID | None = Query(None),
    status: AppointmentStatus | None = Query(None),
    rep_email: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    query = select(Appointment)
    if lead_id:
        query = query.where(Appointment.lead_id == lead_id)
    if status:
        query = query.where(Appointment.status == status)
    if rep_email:
        query = query.where(Appointment.rep_email == rep_email)
    query = query.order_by(Appointment.scheduled_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{appointment_id}", response_model=AppointmentResponse, dependencies=[Depends(verify_api_key)])
async def get_appointment(appointment_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    appt = await db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


@router.post("", response_model=AppointmentResponse, status_code=201, dependencies=[Depends(verify_api_key)])
async def create_appointment(data: AppointmentCreate, db: AsyncSession = Depends(get_db)):
    appt = Appointment(**data.model_dump())
    db.add(appt)
    await db.commit()
    await db.refresh(appt)
    return appt


@router.patch("/{appointment_id}", response_model=AppointmentResponse, dependencies=[Depends(verify_api_key)])
async def update_appointment(
    appointment_id: uuid.UUID,
    data: AppointmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    appt = await db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(appt, field, value)
    await db.commit()
    await db.refresh(appt)
    return appt
