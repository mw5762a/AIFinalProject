from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai

# Gemini API configuration 
genai.configure(api_key="AIzaSyDqbfXw-dr0B__6lxd30fbsW9YixI2iKeo")

def analyze_journal_entry(entry):
    prompt = f"""
    Analyze the following journal entry for patterns related to mental health challenges.
    For the output: 
    - Provide one sentence describing the possible mental health challenge. 
    - List 2-3 coping mechanisms in a bulleted format.
    Entry: {entry}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    # Make sure response is valid 
    if response and response.text:
        lines = response.text.strip().split("\n")
        challenge_description = "No specific challenge detected."
        coping_mechanisms = []

        #first line is the sentence of the challenges 
        if lines:
            challenge_description = lines[0]
            
        for line in lines[1:]:
            if line.startswith("-") or line.startswith("*"):
                coping_mechanism = line.lstrip("-* ").strip()
                coping_mechanisms.append(coping_mechanism)

        return challenge_description, coping_mechanisms
    else:
        return "No analysis available.", []
    

def get_local_recommendations(location, coping_mechanisms):
    prompt = f"""
    The user is located at {location}. Given the following coping mechanisms: {coping_mechanisms}, 
    what are some local resources in the area that can aid these coping mechanisms?
    Please provide 2-3 specific recommendations in a bulleted list format.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    # Print the full response for debugging
    print("Full response:", response)

    # Check if the response has candidates and handle accordingly
    if response and hasattr(response, 'candidates') and response.candidates:
        # Debugging: Print the first candidate to check its structure
        print("First candidate structure:", response.candidates[0])

        # Assuming 'response.candidates[0]' is a proto object, access it directly
        # If it's not a dictionary, you need to handle it accordingly
        try:
            content = response.candidates[0].content.parts[0].text.strip()
            print("Content extracted from response:", content)

            recommendations = []
            sections = content.split("\n\n")  # Split by paragraphs

            for section in sections:
                # Split by individual lines
                lines = section.split("\n")
                for line in lines:
                    # Look for bullet points (start with "*")
                    if line.strip().startswith("*"):
                        recommendation = line.strip("* ").strip()  # Clean the bullet point
                        recommendations.append(recommendation)

            print("Recommendations extracted:", recommendations)

            # Return recommendations or a default message if none found
            return recommendations if recommendations else ["No local recommendations available."]
        except Exception as e:
            print(f"Error while extracting content: {e}")
            return ["No local recommendations available."]
    else:
        print("Error: Missing expected response structure.")
        return ["No local recommendations available."]

def journal_form_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        entry = request.POST.get('entry')

        # Get AI analysis of the journal entry
        challenge_description, coping_mechanisms = analyze_journal_entry(entry)

        # Get local recommendations based on the coping mechanisms
        local_recommendations = get_local_recommendations(location, coping_mechanisms)

        print("Local Recommendations:", local_recommendations)

        return render(request, 'results.html', {
            'name': name,
            'location': location,
            'challenge_description': challenge_description,
            'coping_mechanisms': coping_mechanisms,
            'local_recommendations': local_recommendations
        })

    return render(request, 'index.html')
