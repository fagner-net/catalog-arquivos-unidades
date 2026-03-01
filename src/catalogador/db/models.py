"""SQLAlchemy ORM models for the catalogador application."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Shared declarative base for all models."""


class StorageUnit(Base):
    """A registered storage unit (physical disk, NAS, Google Drive, etc.)."""

    __tablename__ = "storage_units"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    alias: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    unit_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    scan_sessions: Mapped[list["ScanSession"]] = relationship(
        back_populates="storage_unit", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<StorageUnit(alias={self.alias!r}, type={self.unit_type!r})>"


class ScanSession(Base):
    """A single scan execution against a storage unit."""

    __tablename__ = "scan_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    storage_unit_id: Mapped[int] = mapped_column(ForeignKey("storage_units.id"), nullable=False)
    root_path: Mapped[str] = mapped_column(Text, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_files: Mapped[int | None] = mapped_column(nullable=True)
    total_errors: Mapped[int | None] = mapped_column(nullable=True)

    storage_unit: Mapped["StorageUnit"] = relationship(back_populates="scan_sessions")
    file_records: Mapped[list["FileRecord"]] = relationship(
        back_populates="scan_session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<ScanSession(unit={self.storage_unit_id}, "
            f"root={self.root_path!r}, started={self.started_at})>"
        )


class FileRecord(Base):
    """Metadata record for a single cataloged file."""

    __tablename__ = "file_records"
    __table_args__ = (UniqueConstraint("scan_session_id", "full_path", name="uq_session_path"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scan_session_id: Mapped[int] = mapped_column(ForeignKey("scan_sessions.id"), nullable=False)
    full_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    extension: Mapped[str] = mapped_column(String(20), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    hash_algorithm: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at_os: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    modified_at_os: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cataloged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    scan_session: Mapped["ScanSession"] = relationship(back_populates="file_records")

    def __repr__(self) -> str:
        return f"<FileRecord(name={self.file_name!r}, size={self.size_bytes})>"
