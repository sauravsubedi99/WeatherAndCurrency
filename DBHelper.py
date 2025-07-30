import sqlite3
from datetime import datetime
from DBConfig import get_db_config

class DBHelper:
    """Database helper class for managing customer data"""
    
    def __init__(self):
        """Initialize database helper with configuration"""
        self.config = get_db_config()
        self.db_name = self.config['database_name']
        self.table_name = self.config['table_name']
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create customers table
            create_table_query = f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            '''
            
            cursor.execute(create_table_query)
            conn.commit()
            conn.close()
            
            print(f"Database '{self.db_name}' initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False
    
    def insert_customer(self, customer_name):
        """Insert a new customer into the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            insert_query = f'''
            INSERT INTO {self.table_name} (customer_name, date_added)
            VALUES (?, ?)
            '''
            
            cursor.execute(insert_query, (customer_name, datetime.now()))
            conn.commit()
            
            # Get the ID of the inserted record
            customer_id = cursor.lastrowid
            conn.close()
            
            print(f"Customer '{customer_name}' inserted with ID: {customer_id}")
            return True
            
        except Exception as e:
            print(f"Error inserting customer: {e}")
            return False
    
    def get_all_customers(self):
        """Retrieve all customers from the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            select_query = f'''
            SELECT id, customer_name, date_added 
            FROM {self.table_name} 
            ORDER BY date_added DESC
            '''
            
            cursor.execute(select_query)
            customers = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            customers_list = []
            for customer in customers:
                customers_list.append({
                    'id': customer['id'],
                    'customer_name': customer['customer_name'],
                    'date_added': customer['date_added']
                })
            
            return customers_list
            
        except Exception as e:
            print(f"Error retrieving customers: {e}")
            return []
    
    def get_customer_by_id(self, customer_id):
        """Retrieve a specific customer by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            select_query = f'''
            SELECT id, customer_name, date_added 
            FROM {self.table_name} 
            WHERE id = ?
            '''
            
            cursor.execute(select_query, (customer_id,))
            customer = cursor.fetchone()
            conn.close()
            
            if customer:
                return {
                    'id': customer['id'],
                    'customer_name': customer['customer_name'],
                    'date_added': customer['date_added']
                }
            return None
            
        except Exception as e:
            print(f"Error retrieving customer: {e}")
            return None
    
    def delete_customer(self, customer_id):
        """Delete a specific customer by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            delete_query = f'DELETE FROM {self.table_name} WHERE id = ?'
            cursor.execute(delete_query, (customer_id,))
            
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"Deleted {rows_affected} customer(s)")
            return rows_affected > 0
            
        except Exception as e:
            print(f"Error deleting customer: {e}")
            return False
    
    def clear_all_customers(self):
        """Clear all customers from the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            delete_query = f'DELETE FROM {self.table_name}'
            cursor.execute(delete_query)
            
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"Cleared {rows_affected} customer(s) from database")
            return True
            
        except Exception as e:
            print(f"Error clearing customers: {e}")
            return False
    
    def get_customer_count(self):
        """Get total number of customers in database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            count_query = f'SELECT COUNT(*) as count FROM {self.table_name}'
            cursor.execute(count_query)
            
            result = cursor.fetchone()
            conn.close()
            
            return result['count'] if result else 0
            
        except Exception as e:
            print(f"Error getting customer count: {e}")
            return 0