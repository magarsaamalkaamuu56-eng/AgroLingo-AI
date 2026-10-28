
# Agrolingo AI

A multilingual agricultural assistant powered by the Gemini API.

## Features

- Agricultural question-and-answer chat
- Agricultural terminology translation and simplification
- Crop image analysis
- Multiple response languages
- Responsive mobile-friendly interface
- Flask backend that keeps the Gemini API key server-side

## Requirements

- Python 3
- Google Gemini API key
- GitHub account
- Render account

## Deploy on Render

1. Upload the project files to a GitHub repository.
2. Open https://dashboard.render.com/
3. Select New +, then Web Service.
4. Connect your GitHub repository.
5. Set the build command:

   pip install -r requirements.txt

6. Set the start command:

   gunicorn app:app

7. Add these environment variables in Render:

   GEMINI_API_KEY = your private Gemini API key

   GEMINI_MODEL = gemini-2.5-flash

8. Deploy the service.
9. Open the website URL supplied by Render.

## Project structure

agrolingo-ai/
├── app.py
├── requirements.txt
├── render.yaml
├── README.md
└── templates/
    └── index.html

## Important

Never publish your Gemini API key in HTML or GitHub.

The Market & Weather module requires separate real weather and
agricultural market data sources.

AI crop diagnoses are suggestions and should be verified
when important farming decisions depend on them.
