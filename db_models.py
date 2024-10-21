from sqlalchemy import Column, BIGINT, DOUBLE, String, DATETIME, INT
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DisasterNotification(Base):
    __tablename__ = "disaster_notification"

    sn = Column(INT, nullable=False, primary_key=True)
    message = Column(String, nullable=False)
    region = Column(String, nullable=False)
    created_datetime = Column(DATETIME(6), nullable=False)

    def __init__(self, sn, message, region, created_datetime):
        self.sn = sn
        self.message = message
        self.region = region
        self.created_datetime = created_datetime