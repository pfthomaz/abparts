# backend/app/crud/stocktake.py

from sqlalchemy.orm import Session
from .. import models, schemas

def get_stocktake_locations(db: Session) -> list[schemas.StocktakeLocation]:
    """
    Fetches all unique inventory locations from the database.
    """
    locations = db.query(models.Inventory.location).distinct().all()
    # The result from .all() is a list of tuples, e.g., [('Location A',), ('Location B',)]
    # We need to extract the first element from each tuple.
    return [schemas.StocktakeLocation(name=location[0]) for location in locations if location[0]]

def generate_worksheet_data(db: Session, location: str) -> list[schemas.InventoryResponse]:
    """
    Retrieves all inventory items for a given location to generate a worksheet.
    """
    return db.query(models.Inventory).filter(models.Inventory.location == location).all()
