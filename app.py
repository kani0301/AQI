
from flask import Flask, render_template, request
import requests

TOKEN = "cbfc1c34d298a2c8398bdd9b464717aea55d9a1d"

def geocode_city(city):
    url = "https://nominatim.openstreetmap.org/search"
    params = {'q': city, 'format': 'json', 'limit': 1}
    headers = {'User-Agent': 'MyAirQualityApp'}
    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()
    data = r.json()
    if not data:
        raise ValueError("Could not geocode city")
    lat = float(data[0]['lat'])
    lon = float(data[0]['lon'])
    return lat, lon

def fetch_aqi(lat, lon):
    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={TOKEN}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "ok":
        raise ValueError("AQI data not available at this location")
    return data["data"].get("aqi", 0)

def classify(aqi):
    if aqi <= 50: return "Good"
    if aqi <= 100: return "Moderate"
    if aqi <= 150: return "USG"
    if aqi <= 200: return "Unhealthy"
    if aqi <= 300: return "Very Unhealthy"
    return "Hazardous"

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    city = request.form.get('city', '').strip()
    if not city:
        return render_template('index.html', prediction_text="Please enter a city name.", city=city)

    try:
        lat, lon = geocode_city(city)
        aqi = fetch_aqi(lat, lon)
        aqi_class = classify(aqi)
        prediction_text = f'Predicted AQI for {city}: {int(aqi)} ({aqi_class})'
    except Exception as e:
        try:
            lat, lon = geocode_city(city)
            prediction_text = f"AQI data unavailable for {city}. Showing location only."
            aqi = None
            aqi_class = None
        except:
            return render_template('index.html', prediction_text=f"Could not find location for '{city}'. Please check the name.", city=city)

    return render_template(
        'index.html',
        prediction_text=prediction_text,
        city=city,
        lat=lat,
        lon=lon,
        aqi_class=aqi_class
    )

if __name__ == "__main__":
    app.run(debug=True, port=8080)
