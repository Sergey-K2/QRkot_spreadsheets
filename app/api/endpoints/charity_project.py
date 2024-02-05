from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    charity_project_done,
    check_charityproject_exists,
    check_name_duplicate,
    check_project_invested,
    check_updating_full_sum,
    check_if_none,
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charityproject_crud
from app.crud.donation import donation_crud
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.investment import investing

router = APIRouter()


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    projects = await charityproject_crud.get_multiple(session)
    return projects


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_charity_project(
    charity_project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    check_if_none(charity_project.name)
    check_if_none(charity_project.description)
    await check_name_duplicate(charity_project.name, session)
    new_project = await charityproject_crud.create(charity_project, session,
                                                   commit=False)
    session.add_all(
        investing(
            new_project, await donation_crud.get_not_invested(session)
        )
    )
    await session.commit()
    await session.refresh(new_project)
    return new_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_charity_poject(
    project_id: int,
    object: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    project = await check_charityproject_exists(project_id, session)
    await charity_project_done(project_id, session)
    if object.full_amount is not None:
        await check_updating_full_sum(
            project_id, object.full_amount, session
        )

    if object.name is not None:
        await check_name_duplicate(object.name, session)
    project = await charityproject_crud.update(project, object, session)
    return project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    charity_project = await check_charityproject_exists(project_id, session)
    await check_project_invested(project_id, session)

    charity_project = await charityproject_crud.remove(
        charity_project, session
    )
    return charity_project
