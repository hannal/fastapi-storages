import uuid

import pytest
from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import Session, declarative_base

from sqlalchemy_fields.types import UUID
from tests.engine import database_uri

Base = declarative_base()
engine = create_engine(database_uri)


class Model(Base):
    __tablename__ = "model"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID)


@pytest.fixture(autouse=True)
def prepare_database():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.mark.parametrize(
    "uuid",
    [
        None,
        "12345678-1234-5678-1234-567812345678",
        "12345678123456781234567812345678",
        uuid.UUID("12345678123456781234567812345678"),
    ],
)
def test_valid_uuid(uuid: str | uuid.UUID | None) -> None:
    model = Model(uuid=uuid)

    with Session(engine) as session:
        session.add(model)
        session.commit()


@pytest.mark.parametrize(
    "uuid",
    [
        "",
        "12345678-1234-5678-1234-5678123456780",
        "123456781234567812345678123456780",
    ],
)
def test_invalid_uuid(uuid: str) -> None:
    model = Model(uuid=uuid)

    with Session(engine) as session:
        session.add(model)

        with pytest.raises(StatementError):
            session.commit()
