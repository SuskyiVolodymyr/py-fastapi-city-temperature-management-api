from fastapi import Query
from sqlalchemy.orm import Session

from database import models


def get_all_temperatures(db: Session, city_id: int = None) -> Query:
    if city_id:
        return (
            db.query(models.Temperature)
            .filter(models.Temperature.city_id == city_id)
            .all()
        )
    return db.query(models.Temperature).all()
