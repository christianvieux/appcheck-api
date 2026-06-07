import enum
from sqlalchemy import Enum as SAEnum, Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from services.database import Base

class Project(Base):
    __tablename__ = "projects"
    id            = Column(Integer, primary_key=True)
    name          = Column(String, nullable=False)
    description   = Column(String, nullable=True)
    created_at    = Column(DateTime, default=func.now())
    updated_at    = Column(DateTime, default=func.now(), onupdate=func.now())

class TargetType(str, enum.Enum):
    web_app    = "web_app"
    api        = "api"
    mobile_app = "mobile_app"
    network    = "network"

class Target(Base):
    __tablename__                   = "targets"
    id: Mapped[int]                 = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int]         = mapped_column(
        ForeignKey("projects.id"),
        nullable=False
    )
    name                            = Column(String, nullable=False)
    url                             = Column(String, nullable=False)
    target_type: Mapped[TargetType] = mapped_column(
        SAEnum(TargetType),
        nullable=False
    )
    description                     = Column(String, nullable=True)
    created_at                      = Column(DateTime, default=func.now())
    updated_at                      = Column(DateTime, default=func.now(), onupdate=func.now())