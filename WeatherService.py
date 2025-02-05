import os
import requests
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

class WeatherService:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.headers = {
           
            'Accept': 'application/geo+json'
        }

    def get_grid_points(self, lat, lon):
        """Get the grid points for a specific latitude and longitude"""
        url = f'https://api.weather.gov/points/{lat},{lon}'
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_forecast(self, grid_data):
        """Get the forecast using grid data"""
        forecast_url = grid_data['properties']['forecast']
        response = requests.get(forecast_url, headers=self.headers)
        return response.json()

    def generate_weather_description(self, forecast_data):
        """Use GPT-4 to generate a natural description of the weather"""
        # Extract today's forecast
        today_forecast = forecast_data['properties']['periods'][0]
        
        prompt = f"""Based on this weather data, create a natural, conversational description of today's weather:
        Temperature: {today_forecast['temperature']}°{today_forecast['temperatureUnit']}
        Forecast: {today_forecast['detailedForecast']}
        Please make it sound friendly and conversational, like a weather reporter would say it."""

        response = self.client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL'),
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content

    def create_audio_forecast(self, weather_description):
        """Convert the weather description to speech using OpenAI's text-to-speech"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_file_path = f"weather_forecast_{timestamp}.mp3"

        response = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=weather_description
        )
        
        # Write the binary content directly to the file
        with open(audio_file_path, 'wb') as f:
            f.write(response.content)
        
        return audio_file_path

def main():
    weather_service = WeatherService()
    
    # Example coordinates for New York City
    lat, lon = 40.7128, -74.0060
    
    try:
        # Get weather data
        grid_data = weather_service.get_grid_points(lat, lon)
        forecast_data = weather_service.get_forecast(grid_data)
        
        # Generate description
        weather_description = weather_service.generate_weather_description(forecast_data)
        print("\nGenerated Weather Description:")
        print(weather_description)
        
        # Create audio file
        audio_file = weather_service.create_audio_forecast(weather_description)
        print(f"\nAudio file created: {audio_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 