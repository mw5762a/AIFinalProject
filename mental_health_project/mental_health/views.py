from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from django.views.decorators.csrf import csrf_exempt

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

        #first line of AI output is the sentence of the challenges 
        if lines:
            challenge_description = lines[0]
        
        #remaining lines are going to be the bullet list of coping mechanisms
        for line in lines[1:]:
            if line.startswith("-") or line.startswith("*"):
                coping_mechanism = line.lstrip("-* ").strip()
                coping_mechanisms.append(coping_mechanism)

        return challenge_description, coping_mechanisms
    else:
        return "No analysis available.", []
    
#second generative AI call to get special recommendations 
def get_local_recommendations(location, coping_mechanisms):
    prompt = f"""
    The user is located at {location}. Given the following coping mechanisms: {coping_mechanisms}, 
    what are some local resources in the area that can aid these coping mechanisms?
    Please provide 2-3 specific recommendations in a bulleted list format.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    if response and hasattr(response, 'candidates') and response.candidates:

        try:
            content = response.candidates[0].content.parts[0].text.strip()
            print("Content extracted from response:", content)

            recommendations = []
            sections = content.split("\n\n") 

            for section in sections:
                lines = section.split("\n")
                for line in lines:
                    # Look for bullet points (start with "*") - add to recommendations line by line
                    if line.strip().startswith("*"):
                        recommendation = line.strip("* ").strip() 
                        recommendations.append(recommendation)

            print("Recommendations extracted:", recommendations)

            # Return recommendations or a default message if none found
            if recommendations: 
                return recommendations 
            else: 
                return ["No local recommendations available."]
            
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

        # Call to functions to get generative AI
        challenge_description, coping_mechanisms = analyze_journal_entry(entry)
        local_recommendations = get_local_recommendations(location, coping_mechanisms)

        # Store these results in the session for PDF generation
        request.session['challenge_description'] = challenge_description
        request.session['coping_mechanisms'] = coping_mechanisms
        request.session['location'] = location
        request.session['local_recommendations'] = local_recommendations

        return render(request, 'results.html', {
            'name': name,
            'location': location,
            'challenge_description': challenge_description,
            'coping_mechanisms': coping_mechanisms,
            'local_recommendations': local_recommendations
        })

    return render(request, 'index.html')

def download_pdf(request):
    # Retrieve data from session
    challenge_description = request.session.get('challenge_description', '')
    coping_mechanisms = request.session.get('coping_mechanisms', [])
    location = request.session.get('location', '')
    local_recommendations = request.session.get('local_recommendations', [])

    # Debugging: print the session data
    print(f"Retrieved from session: {challenge_description}, {coping_mechanisms}, {location}, {local_recommendations}")

    # Render the HTML string with the retrieved data
    html_string = render_to_string('pdf_template.html', {
        'challenge_description': challenge_description,
        'coping_mechanisms': coping_mechanisms,
        'location': location,
        'local_recommendations': local_recommendations,
    })

    html = HTML(string=html_string)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="analysis_results.pdf"'
    html.write_pdf(response)

    return response
