from flask import Flask, request, render_template
import requests

app = Flask(__name__)

API_KEY = "5bad89c1b45c5d0e499917d884297394"

def get_coordinates(city):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={API_KEY}"
    res = requests.get(url).json()
    if not res:
        return None, None
    return res[0]['lat'], res[0]['lon']

def fetch_current_data(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    return requests.get(url).json()

def categorize_aqi(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    else:
        return "Poor"

def health_advice(aqi):
    if aqi <= 50:
        return "Safe for all people"
    elif aqi <= 100:
        return "Sensitive groups should be careful"
    else:
        return "Avoid outdoor activity"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict")
def predict():
    city = request.args.get("city")

    if not city:
        return render_template("index.html")

    lat, lon = get_coordinates(city)

    if not lat:
        return render_template("result.html",
                               city=city,
                               aqi=0,
                               category="No Data",
                               pm10=0,
                               pm25=0,
                               ozone=0,
                               primary="No Data",
                               health_advice="No Data",
                               aqi_values=[0]*7)

    data = fetch_current_data(lat, lon)

    if "list" not in data or len(data["list"]) == 0:
        return render_template("result.html",
                               city=city,
                               aqi=0,
                               category="No Data",
                               pm10=0,
                               pm25=0,
                               ozone=0,
                               primary="No Data",
                               health_advice="No Data",
                               aqi_values=[0]*7)

    aqi = data['list'][0]['main']['aqi'] * 50
    pm25 = data['list'][0]['components']['pm2_5']
    pm10 = data['list'][0]['components']['pm10']
    ozone = data['list'][0]['components'].get('o3', 0)

    category = categorize_aqi(aqi)
    advice = health_advice(aqi)

    values = {"PM10": pm10, "PM2.5": pm25, "Ozone": ozone}
    primary = max(values, key=values.get)

    aqi_values = [max(aqi-30,0), max(aqi-20,0), max(aqi-10,0),
                  max(aqi-5,0), max(aqi-2,0), max(aqi-1,0), aqi]

    return render_template("result.html",
                           city=city,
                           aqi=aqi,
                           category=category,
                           pm10=pm10,
                           pm25=pm25,
                           ozone=ozone,
                           primary=primary,
                           health_advice=advice,
                           aqi_values=aqi_values)

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True, host="0.0.0.0", port=5000)
