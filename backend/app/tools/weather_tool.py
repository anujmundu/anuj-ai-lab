from app.connectors.weather_connector import weather_connector


class WeatherTool:

    def get_weather(self):

        return weather_connector.get_weather()


weather_tool = WeatherTool()