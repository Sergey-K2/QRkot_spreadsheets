from typing import Optional, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    async def get_project_id(
        self,
        name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        project_id = await session.execute(
            select(CharityProject.id).where(CharityProject.name == name)
        )
        return project_id.scalars().first()

    async def get_invested_in_project(
        self,
        project_id: int,
        session: AsyncSession,
    ) -> int:
        invested_in_project = await session.execute(
            select(CharityProject.invested_amount).where(
                CharityProject.id == project_id
            )
        )
        return invested_in_project.scalars().first()

    async def get_project_investing_done(
        self,
        project_id: int,
        session: AsyncSession,
    ) -> bool:
        project_investing_done = await session.execute(
            select(CharityProject.fully_invested).where(
                CharityProject.id == project_id
            )
        )
        return project_investing_done.scalars().first()

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession,
    ) -> List[CharityProject]:
        projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested
            ).order_by(
                func.julianday(CharityProject.close_date) -
                func.julianday(CharityProject.create_date)
            )
        )
        return projects.scalars().all()


charityproject_crud = CRUDCharityProject(CharityProject)
