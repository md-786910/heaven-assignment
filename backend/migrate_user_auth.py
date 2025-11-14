"""
Migration script to add authentication fields to users table
Run this after starting the database with docker-compose
"""
from app.core.database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as connection:
        # Add authentication fields to users table
        try:
            print("Adding hashed_password column...")
            connection.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS hashed_password VARCHAR DEFAULT '' NOT NULL;
            """))
            connection.commit()

            print("Adding is_active column...")
            connection.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
            """))
            connection.commit()

            print("Adding reset_code column...")
            connection.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS reset_code VARCHAR NULL;
            """))
            connection.commit()

            print("Adding reset_code_expires column...")
            connection.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS reset_code_expires TIMESTAMP WITH TIME ZONE NULL;
            """))
            connection.commit()

            print("Adding updated_at column...")
            connection.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;
            """))
            connection.commit()

            print("✅ Migration completed successfully!")

        except Exception as e:
            print(f"❌ Error during migration: {e}")
            print("Note: If columns already exist, this is normal.")

if __name__ == "__main__":
    print("Starting migration for user authentication...")
    migrate()
