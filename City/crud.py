from fastapi import Query

from database import models
from City import schemas
from sqlalchemy.orm import Session


def get_all_cities(db: Session) -> Query:
    return db.query(models.City).all()


def create_city(db: Session, city: schemas.CityCreate) -> models.City:
    db_city = models.City(name=city.name, additional_info=city.additional_info)
    db.add(db_city)
    db.commit()
    db.refresh(db_city)

    return db_city


def get_city_by_id(db: Session, city_id: int) -> models.City:
    return db.query(models.City).filter(models.City.id == city_id).first()


def update_city(db: Session, city_id: int, city: schemas.CityCreate) -> models.City:
    db_city = get_city_by_id(db, city_id)
    db_city.name = city.name
    db_city.additional_info = city.additional_info
    db.commit()
    db.refresh(db_city)
    return db_city


def delete_city(db: Session, city_id: int) -> Query:
    db_city = get_city_by_id(db, city_id)
    db.delete(db_city)
    db.commit()
    return db.query(models.City).all()


def get_city_by_name(db: Session, name: str) -> models.City:
    return db.query(models.City).filter(models.City.name == name).first()
