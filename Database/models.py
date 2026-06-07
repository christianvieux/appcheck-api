import enum
from sqlalchemy import Enum as SAEnum, Column, Integer, String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
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

    saved_tests = relationship("SavedTest", back_populates="target")

class TestSuite(Base):
    __tablename__ = "test_suites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    target_id: Mapped[int] = mapped_column(
        ForeignKey("targets.id"),
        nullable=False
    )

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    saved_tests = relationship("SavedTest", back_populates="suite")

class SavedTest(Base):
    __tablename__ = "saved_tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    suite_id: Mapped[int] = mapped_column(
        ForeignKey("test_suites.id"),
        nullable=False
    )

    target_id: Mapped[int] = mapped_column(
        ForeignKey("targets.id"),
        nullable=False
    )

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    method = Column(String, nullable=False)
    path = Column(String, nullable=False)

    headers = Column(JSON, nullable=True)
    query_params = Column(JSON, nullable=True)
    body = Column(JSON, nullable=True)

    expected_status = Column(Integer, nullable=False)
    max_response_time_ms = Column(Integer, nullable=False)

    assertions = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    suite = relationship("TestSuite", back_populates="saved_tests")
    target = relationship("Target", back_populates="saved_tests")