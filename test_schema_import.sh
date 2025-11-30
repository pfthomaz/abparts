#!/bin/bash
docker-compose restart api
sleep 5
docker-compose exec -T api python -c "from app.schemas import StockAdjustmentListResponse; print('SUCCESS')"
