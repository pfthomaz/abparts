# backend/app/routers/stocktake.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud
from ..database import get_db
from ..auth import get_current_user, has_role

router = APIRouter()

@router.get("/locations", response_model=List[schemas.StocktakeLocation], tags=["Stocktake"])
def get_stocktake_locations(
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(get_current_user)
):
    """
    Retrieves all unique locations from the inventory that can be used for a stocktake.
    """
    return crud.stocktake.get_stocktake_locations(db)

@router.post("/worksheet", tags=["Stocktake"])
async def generate_stocktake_worksheet(
    location: schemas.StocktakeLocation, # Request body with location
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(has_role("Oraseas Admin")) # Or other appropriate role
):
    """
    Generates a stocktake worksheet for a given location.
    This is a placeholder and will be implemented later.
    """
    # In a real implementation, this would generate a PDF or CSV file.
    # For now, we'll return a JSON representation of the inventory at that location.
    worksheet_data = crud.stocktake.generate_worksheet_data(db, location.name)
    return {"message": "Stocktake worksheet generated successfully", "data": worksheet_data}
