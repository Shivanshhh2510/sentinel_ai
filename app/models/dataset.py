from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)

    file_path = Column(String, nullable=False)

    rows = Column(Integer)

    columns = Column(Integer)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationship
    owner = relationship("User")