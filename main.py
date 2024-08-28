import asyncio
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from City import crud as city_crud, schemas as city_schemas
from Temperature import crud as temperature_crud, schemas as temperature_schemas
from Temperature.services import fetch_temperature
from database import models
from database.engine import SessionLocal

app = FastAPI()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/cities/", response_model=list[city_schemas.City])
def read_cities(db: Session = Depends(get_db)) -> list[city_schemas.City]:
    return city_crud.get_all_cities(db=db)


@app.post("/cities/", response_model=city_schemas.City)
def create_city(
    city: city_schemas.CityCreate, db: Session = Depends(get_db)
) -> city_schemas.City:
    db_city = city_crud.get_city_by_name(db=db, name=city.name)
    if db_city:
        raise HTTPException(
            status_code=400, detail="City with this name already exists"
        )

    return city_crud.create_city(db=db, city=city)


@app.get("/cities/{city_id}", response_model=city_schemas.City)
def read_city(city_id: int, db: Session = Depends(get_db)) -> city_schemas.City:
    db_city = city_crud.get_city_by_id(db=db, city_id=city_id)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city


@app.put("/cities/{city_id}", response_model=city_schemas.City)
def update_city(
    city_id: int, city: city_schemas.CityCreate, db: Session = Depends(get_db)
) -> city_schemas.City:
    db_city = city_crud.get_city_by_id(db=db, city_id=city_id)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return city_crud.update_city(db=db, city_id=city_id, city=city)


@app.delete("/cities/{city_id}", response_model=list[city_schemas.City])
def delete_city(city_id: int, db: Session = Depends(get_db)) -> list[city_schemas.City]:
    db_city = city_crud.get_city_by_id(db=db, city_id=city_id)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return city_crud.delete_city(db=db, city_id=city_id)


@app.post("/temperature/update/")
async def update_temperature(db: Session = Depends(get_db)) -> dict:
    cities = db.query(models.City).all()
    tasks = [fetch_and_store_temperature(db, city) for city in cities]
    await asyncio.gather(*tasks)
    db.commit()
    return {"message": "Temperatures updated successfully"}


async def fetch_and_store_temperature(db: Session, city: models.City) -> None:
    temperature = await fetch_temperature(city.name)
    temp_record = models.Temperature(
        city_id=city.id, temperature=temperature, date_time=datetime.now()
    )
    db.add(temp_record)


@app.get("/temperatures/", response_model=list[temperature_schemas.Temperature])
def read_temperatures(
    db: Session = Depends(get_db),
) -> list[temperature_schemas.Temperature]:
    return temperature_crud.get_all_temperatures(db=db)
