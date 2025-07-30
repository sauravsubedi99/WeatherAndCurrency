from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# API Configuration - Replace with your actual API keys
WEATHER_API_KEY = "288a2d9e1de3e046336f0c2c99ceb341"  # Replace with your actual API key
EXCHANGE_API_URL = "https://api.exchangerate-api.com/v4/latest"  # Free exchange rate API

# Database configuration
DATABASE = 'customer_database.db'

def init_database():
    """Initialize the database"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        print(" Database initialized successfully")
        return True
    except Exception as e:
        print(f" Database initialization error: {e}")
        return False

def get_all_customers():
    """Get all customers from database"""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, customer_name, date_added FROM customers ORDER BY date_added DESC')
        customers = cursor.fetchall()
        conn.close()
        
        customers_list = []
        for customer in customers:
            customers_list.append({
                'id': customer['id'],
                'customer_name': customer['customer_name'],
                'date_added': customer['date_added']
            })
        
        return customers_list
    except Exception as e:
        print(f" Error getting customers: {e}")
        return []

def insert_customer(customer_name):
    """Insert customer into database"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO customers (customer_name, date_added) VALUES (?, ?)', 
                      (customer_name, datetime.now()))
        conn.commit()
        conn.close()
        print(f" Customer '{customer_name}' added successfully")
        return True
    except Exception as e:
        print(f" Error inserting customer: {e}")
        return False

def clear_all_customers():
    """Clear all customers from database"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM customers')
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        print(f" Cleared {rows_affected} customers from database")
        return True
    except Exception as e:
        print(f" Error clearing customers: {e}")
        return False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/weather', methods=['GET'])
def get_weather():
    """Get weather data from OpenWeatherMap API"""
    city = request.args.get('city', '').strip()
    
    if not city:
        return jsonify({'success': False, 'error': 'City name is required'})
    
    if WEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY_HERE":
        return jsonify({'success': False, 'error': 'Weather API key not configured. Please update WEATHER_API_KEY in app.py'})
    
    try:
        # OpenWeatherMap API call
        weather_url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': WEATHER_API_KEY,
            'units': 'metric'  # Use Celsius
        }
        
        print(f"Fetching weather for: {city}")
        response = requests.get(weather_url, params=params, timeout=10)
        
        if response.status_code == 200:
            weather_data = response.json()
            print(f"Weather data received for {weather_data['name']}")
            
            return jsonify({
                'success': True,
                'city': weather_data['name'],
                'temperature': round(weather_data['main']['temp'], 1),
                'description': weather_data['weather'][0]['description'].title(),
                'humidity': weather_data['main']['humidity'],
                'pressure': weather_data['main']['pressure']
            })
        
        elif response.status_code == 404:
            print(f" City not found: {city}")
            return jsonify({'success': False, 'error': f'City "{city}" not found. Please check spelling and try again.'})
        
        elif response.status_code == 401:
            print(" Invalid API key")
            return jsonify({'success': False, 'error': 'Invalid weather API key. Please check your configuration.'})
        
        else:
            print(f" Weather API error: {response.status_code}")
            return jsonify({'success': False, 'error': f'Weather service error (Code: {response.status_code})'})
    
    except requests.exceptions.Timeout:
        print(" Weather API timeout")
        return jsonify({'success': False, 'error': 'Weather service timeout. Please try again.'})
    
    except requests.exceptions.ConnectionError:
        print(" Weather API connection error")
        return jsonify({'success': False, 'error': 'Unable to connect to weather service. Check your internet connection.'})
    
    except requests.exceptions.RequestException as e:
        print(f" Weather API request error: {e}")
        return jsonify({'success': False, 'error': 'Weather service temporarily unavailable.'})
    
    except Exception as e:
        print(f" Unexpected weather error: {e}")
        return jsonify({'success': False, 'error': 'An unexpected error occurred while fetching weather data.'})

@app.route('/exchange', methods=['GET'])
def get_exchange_rate():
    """Get currency exchange rates from ExchangeRate-API"""
    try:
        from_currency = request.args.get('from', 'USD').upper()
        to_currency = request.args.get('to', 'EUR').upper()
        amount = float(request.args.get('amount', 1))
        
        if amount <= 0:
            return jsonify({'success': False, 'error': 'Amount must be greater than 0'})
        
        print(f"Converting {amount} {from_currency} to {to_currency}")
        
        # ExchangeRate-API call (free service)
        exchange_url = f"{EXCHANGE_API_URL}/{from_currency}"
        response = requests.get(exchange_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if to_currency in data['rates']:
                rate = data['rates'][to_currency]
                converted_amount = amount * rate
                
                print(f"Exchange rate: 1 {from_currency} = {rate} {to_currency}")
                
                return jsonify({
                    'success': True,
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'rate': round(rate, 4),
                    'original_amount': amount,
                    'converted_amount': round(converted_amount, 2)
                })
            else:
                print(f"Currency not supported: {to_currency}")
                return jsonify({'success': False, 'error': f'Currency "{to_currency}" not supported'})
        
        elif response.status_code == 404:
            print(f"Base currency not found: {from_currency}")
            return jsonify({'success': False, 'error': f'Currency "{from_currency}" not supported'})
        
        else:
            print(f"Exchange API error: {response.status_code}")
            return jsonify({'success': False, 'error': 'Unable to fetch current exchange rates'})
    
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid amount. Please enter a valid number.'})
    
    except requests.exceptions.Timeout:
        print("Exchange API timeout")
        return jsonify({'success': False, 'error': 'Exchange rate service timeout. Please try again.'})
    
    except requests.exceptions.ConnectionError:
        print("Exchange API connection error")
        return jsonify({'success': False, 'error': 'Unable to connect to exchange rate service. Check your internet connection.'})
    
    except requests.exceptions.RequestException as e:
        print(f"Exchange API request error: {e}")
        return jsonify({'success': False, 'error': 'Exchange rate service temporarily unavailable.'})
    
    except Exception as e:
        print(f"Unexpected exchange error: {e}")
        return jsonify({'success': False, 'error': 'An unexpected error occurred while fetching exchange rates.'})

@app.route('/add_customer', methods=['POST'])
def add_customer():
    """Add customer to database"""
    customer_name = request.form.get('customer_name', '').strip()
    
    if not customer_name:
        flash('Customer name is required!', 'error')
        return redirect(url_for('index'))
    
    if len(customer_name) < 2:
        flash('Customer name must be at least 2 characters long!', 'error')
        return redirect(url_for('index'))
    
    try:
        success = insert_customer(customer_name)
        if success:
            flash(f'Customer "{customer_name}" added successfully!', 'success')
        else:
            flash('Failed to add customer to database!', 'error')
    except Exception as e:
        print(f"Error in add_customer route: {e}")
        flash('An error occurred while adding the customer.', 'error')
    
    return redirect(url_for('customers'))

@app.route('/customers')
def customers():
    """Display all customers"""
    try:
        customers_list = get_all_customers()
        print(f"Retrieved {len(customers_list)} customers")
        return render_template('customers.html', customers=customers_list)
    except Exception as e:
        print(f"Error in customers route: {e}")
        flash(f'Error retrieving customers: {str(e)}', 'error')
        return render_template('customers.html', customers=[])

@app.route('/clear_customers')
def clear_customers():
    """Clear all customers from database"""
    try:
        success = clear_all_customers()
        if success:
            flash('All customers cleared successfully!', 'success')
        else:
            flash('Failed to clear customers from database!', 'error')
    except Exception as e:
        print(f"Error in clear_customers route: {e}")
        flash('An error occurred while clearing customers.', 'error')
    
    return redirect(url_for('customers'))

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500

if __name__ == '__main__':
    print("Starting Weather & Currency Exchange Application")
    print("=" * 50)
    
    # Check API key configuration
    if WEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY_HERE":
        print("WARNING: Weather API key not configured!")
        print("   Please update WEATHER_API_KEY in app.py with your OpenWeatherMap API key")
        print("   Get your free API key at: https://openweathermap.org/api")
    else:
        print("Weather API key configured")
    
    # Initialize database
    if init_database():
        print("Database ready")
    else:
        print("Database initialization failed")
    
    print("=" * 50)
    print("Open your browser to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    app.run(debug=True, port=5000)