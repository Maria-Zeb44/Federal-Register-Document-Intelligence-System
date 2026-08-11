# test_db_connection.py
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

def test_connection():
    """Test database connection"""
    try:
        # Get database URL from environment
        db_url = os.getenv("DATABASE_URL")
        print(f"📊 Database URL: {db_url}")  # Be careful - this shows your password!
        
        # Try to connect
        conn = psycopg2.connect(db_url)
        
        # Create a cursor
        with conn.cursor() as cur:
            # Run a simple query
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(f"✅ Connected successfully!")
            print(f"📊 PostgreSQL version: {version[0][:50]}...")
            
            # Check if our database exists
            cur.execute("SELECT current_database();")
            db_name = cur.fetchone()
            print(f"📊 Current database: {db_name[0]}")
            
            # Check if tables exist
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cur.fetchall()
            if tables:
                print(f"📊 Tables in database:")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("⚠️ No tables found in the database")
        
        # Close connection
        conn.close()
        print("✅ Connection closed properly")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Possible reasons:")
        print("   1. PostgreSQL is not running")
        print("   2. Wrong host/port (check if using localhost:5432)")
        print("   3. Wrong username or password")
        print("   4. Database doesn't exist")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_connection()