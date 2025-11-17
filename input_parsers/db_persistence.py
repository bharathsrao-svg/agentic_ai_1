"""
Database persistence layer for stock holdings
Stores parsed holdings data in PostgreSQL database
"""
import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import sql
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import os

from .models import HoldingsData, StockHolding


class HoldingsDBPersistence:
    """Handles persistence of holdings data to PostgreSQL database"""
    
    def __init__(self, db_config: Optional[dict] = None):
        """
        Initialize database connection
        
        Args:
            db_config: Dictionary with database connection parameters:
                - host: Database host (default: localhost)
                - port: Database port (default: 5432)
                - database: Database name (default: demo_db)
                - user: Database user
                - password: Database password
        """
        if db_config is None:
            db_config = self._load_config_from_env()
        
        self.db_config = db_config
        self.connection = None
    
    def _load_config_from_env(self) -> dict:
        """Load database configuration from environment variables"""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'demo_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
    
    def connect(self):
        """Establish database connection"""
        try:
            # Validate password is not None/empty
            password = self.db_config.get('password') or ''
            
            # Build connection parameters
            conn_params = {
                'host': self.db_config.get('host', 'localhost'),
                'port': self.db_config.get('port', '5432'),
                'database': self.db_config.get('database', 'demo_db'),
                'user': self.db_config.get('user', 'postgres'),
            }
            
            # Only add password if it's provided
            if password:
                conn_params['password'] = password
            
            self.connection = psycopg2.connect(**conn_params)
            self.connection.autocommit = False
            return True
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            if 'password' in error_msg.lower() or 'authentication' in error_msg.lower():
                print(f"Database authentication error: {e}")
                print("Please check your database credentials in db_config.env or environment variables")
            else:
                print(f"Database connection error: {e}")
            raise
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        
        try:
            # Table for holdings import sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS holdings_imports (
                    id SERIAL PRIMARY KEY,
                    source_file VARCHAR(500) NOT NULL UNIQUE,
                    parse_date TIMESTAMP NOT NULL,
                    total_value NUMERIC(15, 2),
                    total_holdings INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index on source_file for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_holdings_imports_source_file 
                ON holdings_imports(source_file)
            """)
            
            # Table for individual holdings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS holdings (
                    id SERIAL PRIMARY KEY,
                    import_id INTEGER REFERENCES holdings_imports(id) ON DELETE CASCADE,
                    symbol VARCHAR(500) NOT NULL,
                    company_name VARCHAR(500),
                    quantity NUMERIC(15, 4),
                    price NUMERIC(15, 4),
                    value NUMERIC(15, 2),
                    sector VARCHAR(200),
                    exchange VARCHAR(100),
                    currency VARCHAR(10),
                    holding_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(import_id, symbol)
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_holdings_symbol ON holdings(symbol)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_holdings_import_id ON holdings(import_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_holdings_sector ON holdings(sector)
            """)
            
            self.connection.commit()
            print("Tables created successfully")
            
        except Exception as e:
            self.connection.rollback()
            print(f"Error creating tables: {e}")
            raise
        finally:
            cursor.close()
    
    def migrate_to_idempotent(self):
        """Migrate existing tables to support idempotent upserts"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        
        try:
            # Drop old unique constraint if it exists
            cursor.execute("""
                ALTER TABLE holdings_imports 
                DROP CONSTRAINT IF EXISTS holdings_imports_source_file_parse_date_key
            """)
            
            # Add unique constraint on source_file only
            cursor.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = 'holdings_imports_source_file_key'
                    ) THEN
                        ALTER TABLE holdings_imports 
                        ADD CONSTRAINT holdings_imports_source_file_key UNIQUE (source_file);
                    END IF;
                END $$;
            """)
            
            # Add updated_at column if it doesn't exist
            cursor.execute("""
                ALTER TABLE holdings_imports 
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            
            # Create index on source_file
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_holdings_imports_source_file 
                ON holdings_imports(source_file)
            """)
            
            self.connection.commit()
            print("Migration to idempotent schema completed successfully")
            
        except Exception as e:
            self.connection.rollback()
            print(f"Error during migration: {e}")
            raise
        finally:
            cursor.close()
    
    def alter_table_columns(self):
        """Alter existing table columns to increase size (for existing databases)"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        
        try:
            # Alter symbol column to allow longer values
            cursor.execute("""
                ALTER TABLE holdings 
                ALTER COLUMN symbol TYPE VARCHAR(500)
            """)
            
            # Alter exchange column to allow longer values
            cursor.execute("""
                ALTER TABLE holdings 
                ALTER COLUMN exchange TYPE VARCHAR(200)
            """)
            
            self.connection.commit()
            print("Table columns altered successfully")
            
        except Exception as e:
            self.connection.rollback()
            # If column doesn't exist or already has correct type, that's okay
            if 'does not exist' not in str(e) and 'already' not in str(e).lower():
                print(f"Error altering table columns: {e}")
                raise
            else:
                print(f"Column alteration skipped: {e}")
        finally:
            cursor.close()
    
    def save_holdings(self, holdings_data: HoldingsData, upsert: bool = True) -> int:
        """
        Save holdings data to database with idempotency support
        
        Args:
            holdings_data: HoldingsData object to save
            upsert: If True, update existing import if same file is parsed again (default: True)
            
        Returns:
            import_id: The ID of the created or updated import record
        """
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        
        try:
            import_id = None
            is_update = False
            
            if upsert:
                # Check if import already exists for this source file
                cursor.execute("""
                    SELECT id, parse_date, total_holdings 
                    FROM holdings_imports 
                    WHERE source_file = %s
                """, (holdings_data.source_file,))
                
                existing = cursor.fetchone()
                
                if existing:
                    import_id = existing[0]
                    is_update = True
                    print(f"Found existing import (id: {import_id}) for file: {holdings_data.source_file}")
                    print(f"  Previous parse date: {existing[1]}")
                    print(f"  Previous holdings count: {existing[2]}")
                    
                    # Delete existing holdings for this import
                    cursor.execute("""
                        DELETE FROM holdings WHERE import_id = %s
                    """, (import_id,))
                    print(f"  Deleted {cursor.rowcount} existing holdings")
                    
                    # Update import record
                    cursor.execute("""
                        UPDATE holdings_imports 
                        SET parse_date = %s,
                            total_value = %s,
                            total_holdings = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (
                        holdings_data.parse_date,
                        holdings_data.total_value,
                        len(holdings_data.holdings),
                        import_id
                    ))
                    print(f"  Updated import record")
            
            if not is_update:
                # Insert new import record
                cursor.execute("""
                    INSERT INTO holdings_imports (source_file, parse_date, total_value, total_holdings)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (source_file) 
                    DO UPDATE SET
                        parse_date = EXCLUDED.parse_date,
                        total_value = EXCLUDED.total_value,
                        total_holdings = EXCLUDED.total_holdings,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                """, (
                    holdings_data.source_file,
                    holdings_data.parse_date,
                    holdings_data.total_value,
                    len(holdings_data.holdings)
                ))
                
                result = cursor.fetchone()
                if result:
                    import_id = result[0]
                else:
                    # If no result, fetch the id from the updated row
                    cursor.execute("""
                        SELECT id FROM holdings_imports WHERE source_file = %s
                    """, (holdings_data.source_file,))
                    import_id = cursor.fetchone()[0]
            
            # Prepare holdings data for bulk insert
            holdings_list = []
            for holding in holdings_data.holdings:
                holdings_list.append((
                    import_id,
                    holding.symbol,
                    holding.company_name,
                    holding.quantity,
                    holding.price,
                    holding.value,
                    holding.sector,
                    holding.exchange,
                    holding.currency,
                    holding.date.date() if holding.date else None
                ))
            
            # Bulk insert holdings (always insert, since we deleted old ones if updating)
            if holdings_list:
                execute_values(
                    cursor,
                    """
                    INSERT INTO holdings 
                    (import_id, symbol, company_name, quantity, price, value, 
                     sector, exchange, currency, holding_date)
                    VALUES %s
                    """,
                    holdings_list
                )
            
            self.connection.commit()
            action = "Updated" if is_update else "Saved"
            print(f"{action} {len(holdings_data.holdings)} holdings (import_id: {import_id})")
            return import_id
            
        except Exception as e:
            self.connection.rollback()
            print(f"Error saving holdings: {e}")
            raise
        finally:
            cursor.close()
    
    def get_latest_imports(self, limit: int = 10) -> List[dict]:
        """Get latest import records"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                SELECT id, source_file, parse_date, total_value, total_holdings, created_at
                FROM holdings_imports
                ORDER BY parse_date DESC
                LIMIT %s
            """, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        except Exception as e:
            print(f"Error fetching imports: {e}")
            raise
        finally:
            cursor.close()
    
    def get_holdings_by_import_id(self, import_id: int) -> List[dict]:
        """Get all holdings for a specific import"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                SELECT id, symbol, company_name, quantity, price, value, 
                       sector, exchange, currency, holding_date
                FROM holdings
                WHERE import_id = %s
                ORDER BY value DESC NULLS LAST
            """, (import_id,))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        except Exception as e:
            print(f"Error fetching holdings: {e}")
            raise
        finally:
            cursor.close()
    
    def get_all_holdings_summary(self) -> dict:
        """Get summary of all holdings across all imports"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        
        try:
            # Get total portfolio value
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT import_id) as total_imports,
                    COUNT(*) as total_holdings,
                    SUM(value) as total_portfolio_value,
                    COUNT(DISTINCT symbol) as unique_symbols,
                    COUNT(DISTINCT sector) as unique_sectors
                FROM holdings
            """)
            
            summary = dict(zip([desc[0] for desc in cursor.description], cursor.fetchone()))
            
            # Get top holdings by value
            cursor.execute("""
                SELECT symbol, company_name, SUM(value) as total_value, 
                       COUNT(*) as occurrence_count
                FROM holdings
                GROUP BY symbol, company_name
                ORDER BY total_value DESC
                LIMIT 10
            """)
            
            columns = [desc[0] for desc in cursor.description]
            top_holdings = []
            for row in cursor.fetchall():
                top_holdings.append(dict(zip(columns, row)))
            
            summary['top_holdings'] = top_holdings
            
            return summary
            
        except Exception as e:
            print(f"Error fetching summary: {e}")
            raise
        finally:
            cursor.close()

