from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charityproject_crud
from app.models import CharityProject


NAME_ALREADY_EXISTS_MESSAGE = 'Проект с таким именем уже существует!'
REQUIRED_TOTAL_LOW_MESSAGE = (
    'Требуемая сумма не должна быть меньше уже внесенной!'
)
PROJECT_NOT_FOUND_MESSAGE = 'Проект не найден!'
CANT_DELETE_INVESTED_PROJECT_MESSAGE = (
    'В проект были внесены средства, не подлежит удалению!'
)
CANT_EDIT_CLOSED_PROJECT_MESSAGE = 'Закрытый проект нельзя редактировать!'
FIELD_IS_NONE_MESSAGE = 'Поле не может быть пустым!'


async def check_name_duplicate(
    project: str,
    session: AsyncSession,
) -> None:
    project_id = await charityproject_crud.get_project_id(
        project, session
    )
    if project_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=NAME_ALREADY_EXISTS_MESSAGE,
        )


async def charity_project_done(
    project_id: int,
    session: AsyncSession,
) -> None:
    project_done = await charityproject_crud.get_project_investing_done(
        project_id, session
    )
    if project_done:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=CANT_EDIT_CLOSED_PROJECT_MESSAGE,
        )


async def check_updating_full_sum(
    project_id: int,
    updating_full_amount: int,
    session: AsyncSession,
) -> None:
    invested_amount = await charityproject_crud.get_invested_in_project(
        project_id, session
    )
    if updating_full_amount < invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=REQUIRED_TOTAL_LOW_MESSAGE,
        )


def check_if_none(
        object: str,
) -> None:
    if object is None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=FIELD_IS_NONE_MESSAGE
        )


async def check_charityproject_exists(
    charityproject_id: int,
    session: AsyncSession,
) -> CharityProject:
    project = await charityproject_crud.get(charityproject_id, session)
    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=PROJECT_NOT_FOUND_MESSAGE
        )
    return project


async def check_project_invested(
    project_id: int, session: AsyncSession
) -> None:
    invested_project = await charityproject_crud.get_invested_in_project(
        project_id, session
    )

    if invested_project:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=CANT_DELETE_INVESTED_PROJECT_MESSAGE,
        )
