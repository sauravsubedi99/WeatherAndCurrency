"""
Database Configuration Module
This module contains database configuration settings and connection parameters.
"""

import os

def get_db_config():
    """
    Returns database configuration dictionary.
    This function centralizes all database-related configuration.
    
    Returns:
        dict: Database configuration parameters
    """
    
    # Database configuration settings
    config = {
        # Database file name (SQLite)
        'database_name': 'customer_database.db',
        
        # Main table name for customers
        'table_name': 'customers',
        
        # Database type
        'db_type': 'sqlite',
        
        # Connection timeout (seconds)
        'connection_timeout': 30,
        
        # Enable foreign key constraints
        'foreign_keys': True,
        
        # Database file path (current directory by default)
        'db_path': os.path.join(os.getcwd(), 'customer_database.db'),
        
        # Backup settings
        'backup_enabled': True,
        'backup_interval': 24,  # hours
        
        # Connection pool settings (for future scaling)
        'max_connections': 10,
        'min_connections': 1,
        
        # Logging settings
        'log_queries': False,
        'log_errors': True
    }
    
    return config

def get_table_schema():
    """
    Returns the database table schema definitions.
    
    Returns:
        dict: Table schemas
    """
    
    schemas = {
        'customers': {
            'table_name': 'customers',
            'columns': [
                {
                    'name': 'id',
                    'type': 'INTEGER',
                    'constraints': 'PRIMARY KEY AUTOINCREMENT'
                },
                {
                    'name': 'customer_name',
                    'type': 'TEXT',
                    'constraints': 'NOT NULL'
                },
                {
                    'name': 'date_added',
                    'type': 'TIMESTAMP',
                    'constraints': 'DEFAULT CURRENT_TIMESTAMP'
                }
            ],
            'indexes': [
                'CREATE INDEX IF NOT EXISTS idx_customer_name ON customers(customer_name)',
                'CREATE INDEX IF NOT EXISTS idx_date_added ON customers(date_added)'
            ]
        }
    }
    
    return schemas

def get_api_config():
    """
    Returns API configuration for external services.
    Note: In production, these should be environment variables.
    
    Returns:
        dict: API configuration
    """
    
    api_config = {
        'weather_api': {
            'base_url': 'http://api.openweathermap.org/data/2.5',
            'api_key': os.environ.get('WEATHER_API_KEY', 'your_openweather_api_key'),
            'units': 'metric',
            'timeout': 10
        },
        'exchange_api': {
            'base_url': 'https://api.exchangerate-api.com/v4/latest',
            'api_key': os.environ.get('EXCHANGE_API_KEY', 'your_exchangerate_api_key'),
            'timeout': 10
        }
    }
    
    return api_config

def validate_config():
    """
    Validates the database configuration.
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    
    config = get_db_config()
    
    # Check required fields
    required_fields = ['database_name', 'table_name', 'db_type']
    
    for field in required_fields:
        if field not in config or not config[field]:
            print(f"Error: Missing required configuration field: {field}")
            return False
    
    # Check database path permissions
    db_dir = os.path.dirname(config['db_path'])
    if not os.access(db_dir, os.W_OK):
        print(f"Error: No write permission for database directory: {db_dir}")
        return False
    
    return True

# Environment-specific configurations
def get_development_config():
    """Development environment configuration"""
    config = get_db_config()
    config.update({
        'database_name': 'dev_customer_database.db',
        'log_queries': True,
        'debug': True
    })
    return config

def get_production_config():
    """Production environment configuration"""
    config = get_db_config()
    config.update({
        'database_name': 'prod_customer_database.db',
        'log_queries': False,
        'debug': False,
        'connection_timeout': 60
    })
    return config

def get_test_config():
    """Test environment configuration"""
    config = get_db_config()
    config.update({
        'database_name': ':memory:',  # In-memory database for testing
        'log_queries': True,
        'debug': True
    })
    return config