class WeatherConnector:

    def get_weather(self):

        return {
            "city": "Bhopal",
            "temperature": "30°C",
            "condition": "Sunny"
        }


weather_connector = WeatherConnector()