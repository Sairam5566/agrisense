"""
Database migration script to add new columns and tables for marketplace functionality
"""

import sqlite3
import os

def migrate_database():
    db_path = "./agriculture_portal.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Starting database migration...")
        
        # Check if buyer_requirements table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='buyer_requirements'")
        if not cursor.fetchone():
            print("buyer_requirements table not found!")
            return False
        
        # Check if is_satisfied column exists in buyer_requirements table
        cursor.execute("PRAGMA table_info(buyer_requirements)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current buyer_requirements columns: {columns}")
        
        if 'is_satisfied' not in columns:
            print("Adding is_satisfied column to buyer_requirements table...")
            cursor.execute("ALTER TABLE buyer_requirements ADD COLUMN is_satisfied BOOLEAN DEFAULT 0")
            print("✓ is_satisfied column added")
        else:
            print("✓ is_satisfied column already exists")
            
        if 'satisfied_by_farmer_id' not in columns:
            print("Adding satisfied_by_farmer_id column to buyer_requirements table...")
            cursor.execute("ALTER TABLE buyer_requirements ADD COLUMN satisfied_by_farmer_id INTEGER")
            print("✓ satisfied_by_farmer_id column added")
        else:
            print("✓ satisfied_by_farmer_id column already exists")
        
        # Check if farmer_proposals table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='farmer_proposals'")
        if not cursor.fetchone():
            print("Creating farmer_proposals table...")
            cursor.execute("""
                CREATE TABLE farmer_proposals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farmer_id INTEGER NOT NULL,
                    buyer_requirement_id INTEGER NOT NULL,
                    proposed_quantity REAL NOT NULL,
                    proposed_price_per_unit REAL NOT NULL,
                    unit VARCHAR(20) NOT NULL DEFAULT 'kg',
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✓ farmer_proposals table created")
        else:
            print("✓ farmer_proposals table already exists")
        
        conn.commit()
        print("\n🎉 Database migration completed successfully!")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(buyer_requirements)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"Updated buyer_requirements columns: {new_columns}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\n✅ Migration successful! You can now restart your FastAPI server.")
    else:
        print("\n❌ Migration failed! Please check the errors above.")
