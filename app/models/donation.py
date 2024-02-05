from sqlalchemy import Column, ForeignKey, Integer, Text

from .base import BaseCharityDonation


class Donation(BaseCharityDonation):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)

    OUTPUT = 'Пожертвовал пользователь {user_id} {base}'

    def __repr__(self):
        return self.OUT_DONATION.format(
            user_id=self.user_id,
            base=super().__repr__())
