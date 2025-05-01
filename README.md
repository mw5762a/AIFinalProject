# Generative AI Journal Platform

## Overview 
The Generative AI Journal Platform is designed to provide users with instant and specialized mental health recommendations based on their journal entries. These recommendations are further tailored to their geographic location. By leveraging Gemini's generative AI model, the platform analyzes user input to identify potential mental health challenges, suggest coping mechanisms, and provide local resources to support these strategies.

## Features
Personalized Recommendations: AI-generated insights based on journal entries.

Location-Based Support: Tailored resources relevant to the user's geographic location.

Seamless User Experience: Built using Django's form framework for ease of use and styling.

## User Input Fields

1. Name

2. Geographic Location (generated with user consent via OpenStreetMap's API)

3. Journal Entry

## How it Works 
1. The user submits a journal entry along with their name and geographic location.

2. The backend processes the journal entry using Gemini's AI model to generate:

3. A sentence summarizing possible mental health challenges.

4. A list of 2-3 suggested coping mechanisms.

5. The system then cross-references the user's geographic location with the generated coping mechanisms to provide 2-3 relevant local resources in a bulleted list.

The program will also track your identified mental health challenges on the backend, when the program sees the same challenge three or more times, the user is notified and given additional support recommendations. 

## How to Run it
Clone the repository: git clone https://github.com/mw5762a/AIFinalProject.git

Navigate to the project directory: cd AIFinalProject

Download necessary libraries: pip install -r requirements.txt

Run the server: python manage.py runserver

Open the application in your browser at http://127.0.0.1:8000/
