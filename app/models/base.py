from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, CheckConstraint

from app.core.db import Base


class BaseCharityDonation(Base):
    __abstract__ = True
    __table_args__ = (CheckConstraint('0 <= invested_amount <= full_amount'),
                      CheckConstraint('full_amount > 0'))

    full_amount = Column(Integer, default=0)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)

    OUTPUT = (
        'Пожертвовано на проект: {invested} из {full} '
        'Статус проекта: {status} '
        'Дата открытия проекта: {create_date} '
        'Дата закрытия проекта: {close_date} '
    )

    def __repr__(self):
        return self.OUTPUT.format(
            invested=self.invested_amount,
            full=self.full_amount,
            status=self.fully_invested,
            create_date=self.create_date,
            close_date=self.close_date
        )