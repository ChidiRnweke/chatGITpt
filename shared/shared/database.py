from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKeyConstraint,
    String,
    Integer,
    ForeignKey,
    Table,
)
from pgvector.sqlalchemy import Vector
from alembic.config import Config
from alembic import command
from logging import Logger


def run_migrations(location: str, logger: Logger | None = None) -> None:

    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", location)
    command.upgrade(alembic_cfg, "head")
    if logger:
        logger.info("Migrations run successfully")


class Base(DeclarativeBase):
    pass


class LanguagesModel(Base):
    __tablename__ = "github_languages"

    language: Mapped[str] = mapped_column(String(255), primary_key=True)


languages_repository_bridge = Table(
    "languages_repository_bridge",
    Base.metadata,
    Column("language_name", String(255), primary_key=True),
    Column("repository_name", String(255), primary_key=True),
    Column("repository_user", String(255), primary_key=True),
    ForeignKeyConstraint(
        ["repository_name", "repository_user"],
        [
            "github_repositories.name",
            "github_repositories.user",
        ],
    ),
    ForeignKeyConstraint(
        ["language_name"],
        ["github_languages.language"],
    ),
)


class GitHubRepositoryModel(Base):
    __tablename__ = "github_repositories"

    name: Mapped[str] = mapped_column(String(255), primary_key=True)
    user: Mapped[str] = mapped_column(String(255), primary_key=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    url: Mapped[str] = mapped_column(String(255))

    files: Mapped[list["GithubFileModel"]] = relationship(
        back_populates="repository", cascade="all, delete-orphan"
    )
    languages: Mapped[list[LanguagesModel]] = relationship(
        secondary=languages_repository_bridge
    )


class GithubFileModel(Base):
    __tablename__ = "github_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    content_url: Mapped[str] = mapped_column(String(255))
    last_modified: Mapped[datetime]
    repository_name: Mapped[str] = mapped_column(String(255))
    repository_user: Mapped[str] = mapped_column(String(255))
    file_extension: Mapped[str] = mapped_column(String(255))
    path_in_repo: Mapped[str] = mapped_column(String(255))
    latest_version: Mapped[bool]
    is_embedded: Mapped[bool]

    __table_args__ = (
        ForeignKeyConstraint(
            ["repository_name", "repository_user"],
            [
                "github_repositories.name",
                "github_repositories.user",
            ],
        ),
    )

    repository: Mapped[GitHubRepositoryModel] = relationship(
        back_populates="files", foreign_keys=[repository_name, repository_user]
    )

    embedding: Mapped[list["EmbeddedDocumentModel"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class EmbeddedDocumentModel(Base):
    __tablename__ = "embedded_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("github_files.id"))
    embedding: Mapped[Vector] = mapped_column(Vector(3072))
    input_token_count: Mapped[int]

    __table_args__ = (
        ForeignKeyConstraint(
            ["document_id"],
            ["github_files.id"],
        ),
    )

    document: Mapped[GithubFileModel] = relationship(
        back_populates="embedding",
        foreign_keys=[document_id],
        lazy="joined",
    )


class TokenSpendModel(Base):
    __tablename__ = "tokens_spent"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(255))
    token_count: Mapped[int] = mapped_column(Integer)
    model: Mapped[str] = mapped_column(String(255))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
