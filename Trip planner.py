import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
# use the OpenAI Python package to access Gemini models
# switch to using the standalone gemini package
import gemini
# ChatGPT support via the OpenAI package
import openai
from openai import OpenAI  # explicit class for convenience

# ---------------------------------------------------------------------------
# Agent implementations (replace stubs with real logic as necessary)
# ---------------------------------------------------------------------------

class WeatherAnalysisAgent:
    def __init__(self):
        pass

    def train(self, historical_data):
        # training logic would go here
        pass

    def predict_best_time(self, coord):
        # return dummy data for demonstration
        return [
            {"month": "June", "score": 0.95},
            {"month": "July", "score": 0.90},
        ]


class HotelRecommenderAgent:
    def __init__(self):
        self.hotels = []

    def add_hotels(self, hotels):
        self.hotels = hotels

    def find_hotels(self, preferences):
        # simple slice, real implementation would match preferences
        return self.hotels[:3] if self.hotels else [
            {"name": "Sample Hotel", "description": "A nice stay"}
        ]


class ItineraryPlannerAgent:
    def __init__(self, api_key: str, model: str):
        # model is either "Gemini" or "ChatGPT"
        self.model = model
        if model == "Gemini":
            self.client = gemini.Client(api_key=api_key)
        else:
            # configure OpenAI for ChatGPT
            # use the class imported above or via openai.OpenAI
            self.client = openai.OpenAI(api_key=api_key)

    def create_itinerary(
        self, destination: str, best_month: str, hotel: dict, duration: int
    ) -> str:
        prompt = (
            f"Create a {duration}-day travel itinerary for {destination} "
            f"in the best month: {best_month}. "
            f"Recommended Hotel: {hotel.get('name', 'N/A')}.")

        if self.model == "Gemini":
            response = self.client.responses.create(
                model="gemini-1",
                input=[
                    {"role": "system", "content": "You are an expert travel planner."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
            )
            return response.output_text
        else:
            # ChatGPT path (using OpenAI client)
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert travel planner."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
            )
            return response.choices[0].message.content



# ---------------------------------------------------------------------------
# Streamlit application
# ---------------------------------------------------------------------------

# the secret field still refers to openai but we'll use it for Gemini
# ask the user to supply their own API key via the UI
# the large text area makes it easy to paste a long key
api_key = st.text_area("Enter your API key (Gemini or ChatGPT):", "", height=100)

# allow the user to choose which LLM to use
model_choice = st.selectbox("Choose model to generate itinerary:", ["Gemini", "ChatGPT"])

weather_agent = WeatherAnalysisAgent()
hotel_agent = HotelRecommenderAgent()
# instantiate the itinerary planner only when we have a key
# and know which model to use
itinerary_agent = None

if api_key:
    itinerary_agent = ItineraryPlannerAgent(api_key=api_key, model=model_choice)

# example dataset hooks (replace with actual data loading)
# weather_agent.train(historical_weather_data)
# hotel_agent.add_hotels(hotels_database)

st.title("AI Travel Planner ✈")
st.write("Find the best time to travel and discover the perfect hotel!")

destination = st.text_input("Enter your destination (e.g., Rome):", "Rome")
preferences = st.text_area(
    "Describe your ideal hotel:", "Luxury hotel in city center with spa."
)
duration = st.slider("Trip duration (days):", 1, 14, 5)

if st.button("Generate Travel Plan ✨"):
        if itinerary_agent is None:
            st.error("Please provide an API key before generating a plan.")
        else:
            best_months = weather_agent.predict_best_time(
                {"latitude": 41.9028, "longitude": 12.4964}
            )
            best_month = best_months[0]["month"] if best_months else "Unknown"
            recommended_hotels = hotel_agent.find_hotels(preferences)

            itinerary = itinerary_agent.create_itinerary(
                destination, best_month, recommended_hotels[0], duration
            )

            st.subheader("📆 Best Months to Visit")
            for m in best_months:
                st.write(f"Month {m['month']}: Score {m['score']:.2f}")

            st.subheader("🏨 Recommended Hotel")
            if recommended_hotels:
                h = recommended_hotels[0]
                st.write(f"**{h['name']}** - {h['description']}")
            else:
                st.write("No hotels available.")

            st.subheader("📜 Generated Itinerary")
            st.write(itinerary)
            st.subheader("🗺 Destination Map")
            map_data = pd.DataFrame({"lat": [41.9028], "lon": [12.4964]})
            st.map(map_data)



