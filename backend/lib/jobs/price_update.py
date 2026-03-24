import asyncio
import json
import random
from datetime import datetime
from sqlmodel import Session, select
from lib.database.main import engine
from lib.database.models.metal import Metal
from lib.database.models.market_history import MetalMarketHistory
from lib.websocket_manager import manager
from lib.logger import logger

import yfinance as yf
import httpx

async def fetch_market_price(code: str) -> float:
    """
    Fetches the actual market price from Yahoo Finance via yfinance.
    Mapping: GOLD -> GC=F, SILVER -> SI=F, PLATINUM -> PL=F (Futures contracts)
    """
    logger.debug(f"Fetching market price for {code}...")
    # yfinance is synchronous, but we can run it in a thread to avoid blocking
    ticker = yf.Ticker(code)
    # Get the latest close price
    price_per_ounce = ticker.history(period="1d")['Close'].iloc[-1]
    
    # Conversion: 1 kg = 32.1507 ounces
    price_per_kg = float(price_per_ounce) * 32.1507
    return price_per_kg

async def run_price_update_job(interval_seconds: int = 60):
    """
    Background job to update metal prices from the 'market'.
    """
    print(f"Starting price update job with {interval_seconds}s interval...")
    while True:
        try:
            with Session(engine) as session:
                statement = select(Metal)
                metals = session.exec(statement).all()
                
                if not metals:
                    await asyncio.sleep(5)
                    continue
                
                updates = []
                for metal in metals:
                    new_price = await fetch_market_price(metal.code)
                    
                    metal.current_price_kg = new_price
                    metal.updated_at = datetime.utcnow()
                    session.add(metal)
                    
                    # Log historical data
                    history_entry = MetalMarketHistory(
                        metal_id=metal.id,
                        price_per_kg=new_price
                    )
                    session.add(history_entry)
                    
                    updates.append({
                        "code": metal.code,
                        "price": new_price,
                        "name": metal.name
                    })
                
                session.commit()
                
                logger.info(f"Market prices updated and broadcasted. Count: {len(updates)}")
                
                # Broadcast's message...
                await manager.broadcast(json.dumps({
                    "event_type": "MARKET_UPDATE",
                    "data": updates,
                    "timestamp": datetime.utcnow().isoformat()
                }))
                
        except Exception as e:
            print(f"Error in price update job: {e}")
            
        await asyncio.sleep(interval_seconds)
