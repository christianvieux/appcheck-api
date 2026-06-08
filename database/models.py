import enum
from sqlalchemy import Enum as SAEnum, Column, Integer, String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.database import Base

class Project(Base):
    __tablename__ = "projects"
    id            = Column(Integer, primary_key=True)
    owner_id      = Column(String, nullable=True, index=True)
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

    smoke_tests = relationship("SmokeTest", back_populates="target")
    test_results = relationship("TestResult", back_populates="target")

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

    smoke_tests = relationship("SmokeTest", back_populates="suite", lazy="selectin")
    test_runs = relationship("TestRun", back_populates="suite", lazy="selectin")

class SmokeTest(Base):
    __tablename__ = "smoke_tests"

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

    suite = relationship("TestSuite", back_populates="smoke_tests")
    target = relationship("Target", back_populates="smoke_tests")
    test_results = relationship("TestResult", back_populates="smoke_test")

class TestRun(Base):
    __tablename__ = "test_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    suite_id: Mapped[int] = mapped_column(
        ForeignKey("test_suites.id"),
        nullable=False
    )

    status = Column(String, nullable=False)
    total_tests = Column(Integer, nullable=False)
    passed_count = Column(Integer, nullable=False)
    failed_count = Column(Integer, nullable=False)
    duration_ms = Column(Integer, nullable=False)

    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

    suite = relationship("TestSuite", back_populates="test_runs")
    results = relationship("TestResult", back_populates="test_run", lazy="selectin")

class TestResult(Base):
    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    test_run_id: Mapped[int] = mapped_column(
        ForeignKey("test_runs.id"),
        nullable=False
    )

    saved_test_id: Mapped[int] = mapped_column(
        ForeignKey("smoke_tests.id"),
        nullable=False
    )

    target_id: Mapped[int] = mapped_column(
        ForeignKey("targets.id"),
        nullable=False
    )

    status = Column(String, nullable=False)
    status_code = Column(Integer, nullable=True)
    expected_status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer, nullable=True)
    failure_message = Column(String, nullable=True)
    failure_details = Column(JSON, nullable=True)
    assertion_results = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())

    test_run = relationship("TestRun", back_populates="results")
    smoke_test = relationship("SmokeTest", back_populates="test_results")
    target = relationship("Target", back_populates="test_results")
