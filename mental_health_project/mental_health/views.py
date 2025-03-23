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


#gets the input from the form 
def journal_form_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        entry = request.POST.get('entry')

        challenge_description, coping_mechanisms = analyze_journal_entry(entry)

        return render(request, 'results.html', {
            'name': name,
            'location': location,
            'challenge_description': challenge_description,
            'coping_mechanisms': coping_mechanisms
        })

    return render(request, 'index.html')
