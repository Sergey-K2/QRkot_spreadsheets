from sqlalchemy import Column, String, Text

from .base import BaseCharityDonation


class CharityProject(BaseCharityDonation):
    name = Column(String(110), unique=True, nullable=False)
    description = Column(Text, nullable=False)
