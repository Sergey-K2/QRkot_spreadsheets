from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.charity_project import charityproject_crud
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationCreate, DonationDB, DonationDB_EXT
from app.services.investment import investing

router = APIRouter()


@router.get(
    '/',
    response_model=List[DonationDB_EXT],
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True,
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
):
    donations = await donation_crud.get_not_invested(session)
    return donations


@router.get(
    '/my',
    response_model=List[DonationDB],
    dependencies=[Depends(current_user)],
)
async def get_my_donations(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    donations = await donation_crud.get_donations_by_user(
        user=user, session=session
    )
    return donations


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True)
async def create_new_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    new_donation = await donation_crud.create(donation, session, user, False)
    session.add_all(investing(new_donation,
                    await charityproject_crud.get_multiple(session)))
    await session.commit()
    await session.refresh(new_donation)
    return new_donation
