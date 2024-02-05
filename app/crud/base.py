from typing import Optional, TypeVar, List

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base
from app.models import User

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase:
    def __init__(self, model):
        self.model = model

    async def get(
        self,
        object_id: int,
        session: AsyncSession,
    ):
        db_object = await session.execute(
            select(self.model).where(self.model.id == object_id)
        )
        return db_object.scalars().first()

    async def get_multiple(self, session: AsyncSession):
        db_objects = await session.execute(select(self.model))
        return db_objects.scalars().all()

    async def get_not_invested(
        self,
        session: AsyncSession
    ) -> List[ModelType]:
        not_invested = await session.scalars(
            select(self.model).where(
                self.model.fully_invested == 0
            )
        )
        return not_invested.all()

    async def get_by_attribute(
        self,
        attribute: str,
        attribute_value: str,
        session: AsyncSession,
    ):
        attribute = getattr(self.model, attribute)
        db_object = await session.execute(
            select(self.model).where(attribute == attribute_value)
        )
        return db_object.scalars().first()

    async def create(
        self,
        object,
        session: AsyncSession,
        user: Optional[User] = None,
        commit: bool = True
    ):
        object_in_data = object.dict()
        if user is not None:
            object_in_data['user_id'] = user.id
        db_object = self.model(**object_in_data)
        if db_object.invested_amount is None:
            db_object.invested_amount = 0
        session.add(db_object)
        if commit:
            await session.commit()
            await session.refresh(db_object)
        return db_object

    async def update(
        self,
        db_object,
        object,
        session: AsyncSession,
    ):
        obj_data = jsonable_encoder(db_object)
        update_data = object.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_object, field, update_data[field])
        session.add(db_object)
        await session.commit()
        await session.refresh(db_object)
        return db_object

    async def remove(
        self,
        db_object,
        session: AsyncSession,
    ):
        await session.delete(db_object)
        await session.commit()
        return db_object