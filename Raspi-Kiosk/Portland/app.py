from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Weather model
class WeatherRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

def get_weather():
    api_key = os.getenv('OPENWEATHER_API_KEY')
    portland_lat = "45.5155"
    portland_lon = "-122.6789"
    
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={portland_lat}&lon={portland_lon}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        weather_data = {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description']
        }
        
        # Save to database using SQLAlchemy
        new_record = WeatherRecord(
            temperature=weather_data['temperature'],
            humidity=weather_data['humidity'],
            description=weather_data['description']
        )
        db.session.add(new_record)
        db.session.commit()
        
        return weather_data
    
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

@app.route('/')
def index():
    weather_data = get_weather()
    
    # Get historical data using SQLAlchemy
    history = WeatherRecord.query.order_by(WeatherRecord.timestamp.desc()).limit(10).all()
    
    return render_template('index.html', current_weather=weather_data, history=history)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
