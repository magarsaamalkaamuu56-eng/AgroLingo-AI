import os
from google import genai
from dotenv import load_dotenv

load_dotenv() # Loads local .env file

# Automatically reads GEMINI_API_KEY from environment variables
client = genai.Client() 

def generate_text(prompt):
    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt
    )
    return interaction.output_text
