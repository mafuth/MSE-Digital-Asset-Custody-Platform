from sqlmodel import Session, select
from lib.database.models.vault import Vault
from lib.database.models.metal import Metal
from lib.database.models.account import Account
from lib.database.main import engine, create_db_and_tables
import uuid

def seed_db():
    print("Initializing database and tables...")
    create_db_and_tables()
    with Session(engine) as session:
        # Seed Metals
        existing_metal = session.exec(select(Metal).filter(Metal.code == "XAU")).first()
        if not existing_metal:
            gold = Metal(
                id=uuid.uuid4(),
                code="XAU",
                name="Gold",
                category="Precious Metals",
                current_price_kg=65000.0,
                description="99.9% Pure Investment Grade Gold"
            )
            session.add(gold)
            print("Seeded Gold metal.")
        
        # Seed Maldivian Vaults
        existing_vault = session.exec(select(Vault)).first()
        if not existing_vault:
            vaults = [
                Vault(name="Malé Central Vault", location="Malé, Maldives", capacity_kg=2000.0),
                Vault(name="Hulhumalé Secure Hub", location="Hulhumalé, Maldives", capacity_kg=5000.0),
                Vault(name="Velaana Asset Custody", location="Velaana, Maldives", capacity_kg=1000.0),
            ]
            for v in vaults:
                session.add(v)
            print("Seeded 3 Maldivian vaults.")
        
        session.commit()
        print("Database seeding completed.")

if __name__ == "__main__":
    seed_db()
