from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charityproject_crud
from app.core.google_client import get_service
from app.services.google_api import (set_user_permissions,
                                     spreadsheets_create,
                                     spreadsheets_update_value)

router = APIRouter()


class ValueException(BaseException):
    pass


@router.post(
    '/',
    dependencies=[Depends(current_superuser)],
)
async def get_spreadsheet_report(
        aiogoogle: Aiogoogle = Depends(get_service),
        session: AsyncSession = Depends(get_async_session)
):
    projects = await charityproject_crud.get_projects_by_completion_rate(
        session
    )
    spreadsheet_id, google_url = await spreadsheets_create(aiogoogle)
    await set_user_permissions(spreadsheet_id, aiogoogle)
    try:
        await spreadsheets_update_value(spreadsheet_id, projects, aiogoogle)
    except ValueError as error:
        raise ValueException(
            f"Произошла ошибка {error}", HTTPStatus.BAD_REQUEST
        )
    return google_url + spreadsheet_id
