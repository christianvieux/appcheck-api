import enum
from sqlalchemy import Enum as SAEnum, Column, Integer, String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.database import Base

class Project(Base):
    __tablename__ = "projects"
    id            = Column(Integer, primary_key=True)
    owner_id      = Column(String, nullable=False, index=True)
    name          = Column(String, nullable=False)
    description   = Column(String, nullable=True)
    created_at    = Column(DateTime, default=func.now())
    updated_at    = Column(DateTime, default=func.now(), onupdate=func.now())
    run_results   = relationship(
    "SmokeTestRunResult",
    back_populates="project",
    lazy="selectin",
)

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

    test_suites = relationship("TestSuite", back_populates="target")
    smoke_tests = relationship("SmokeTest", back_populates="target")
    run_results = relationship(
        "SmokeTestRunResult",
        back_populates="target",
        lazy="selectin",
    )

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

    target = relationship("Target", back_populates="test_suites")
    smoke_tests = relationship("SmokeTest", back_populates="suite", lazy="selectin")
    run_results = relationship("SmokeTestRunResult", back_populates="suite", lazy="selectin")

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
    run_results = relationship(
    "SmokeTestRunResult",
    back_populates="smoke_test",
    lazy="selectin",
)

class SmokeTestRunResult(Base):
    __tablename__ = "smoke_test_run_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    run_group_id = Column(String, nullable=False, index=True)
    owner_id = Column(String, nullable=False, index=True)

    smoke_test_id: Mapped[int] = mapped_column(
        ForeignKey("smoke_tests.id"),
        nullable=False,
        index=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )

    suite_id: Mapped[int] = mapped_column(
        ForeignKey("test_suites.id"),
        nullable=False,
        index=True,
    )

    target_id: Mapped[int] = mapped_column(
        ForeignKey("targets.id"),
        nullable=False,
        index=True,
    )

    run_source = Column(String, nullable=False, index=True)
    triggered_by = Column(String, nullable=False, default="manual", index=True)

    name_snapshot = Column(String, nullable=False)
    method_snapshot = Column(String, nullable=False)
    url_snapshot = Column(String, nullable=False)
    path_snapshot = Column(String, nullable=False)
    expected_status_snapshot = Column(Integer, nullable=False)
    max_response_time_ms_snapshot = Column(Integer, nullable=False)
    assertions_snapshot = Column(JSON, nullable=True)
    headers_snapshot = Column(JSON, nullable=True)
    query_params_snapshot = Column(JSON, nullable=True)
    body_snapshot = Column(JSON, nullable=True)

    status = Column(String, nullable=False)
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    failure_message = Column(String, nullable=True)
    failure_details = Column(JSON, nullable=True)
    assertion_results = Column(JSON, nullable=True)

    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    project = relationship("Project", back_populates="run_results")
    target = relationship("Target", back_populates="run_results")
    suite = relationship("TestSuite", back_populates="run_results")
    smoke_test = relationship("SmokeTest", back_populates="run_results")
