from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from django.views.decorators.csrf import csrf_exempt

# Gemini API configuration 
genai.configure(api_key="AIzaSyDqbfXw-dr0B__6lxd30fbsW9YixI2iKeo")
FLAGS = {} 

def analyze_journal_entry(entry):
    prompt = f"""
    Analyze the following journal entry for patterns related to mental health challenges.
    For the output: 
    - Provide a comma seperated list of the mental health challenges present. 
    - List 2-3 coping mechanisms in a bulleted format. The recommendation should be a short one sentence statement.
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
    Please provide 2-3 specific recommendations in a bulleted list format. The recommendation should be no more than one sentence.
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
                return ["No local recommendations."]
            
        except Exception as e:
            print(f"Error while extracting content: {e}")
            return ["No local recommendations available."]
    else:
        print("Error: Missing expected response structure.")
        return ["No local recommendations."]    

def check_flags(flags, name, identified_challenges): 
    global FLAGS
    # Remove .text since identified_challenges is already the string
    lines = identified_challenges.strip().split(", ")
    
    challenges = [] 
    for line in lines:
        # Look for bullet points (start with "*") - add to recommendations line by line
        if line.strip().startswith("*"):
            item = line.strip("* ").strip() 
            challenges.append(item)
        else:
            # Also add non-bullet items (the comma-separated challenges)
            challenges.append(line.strip())

    report = [] #add to report if challenge has been detected more than 3 times. 
    #go through each extracted challenge and see if there is an instance for the user yet 
    for challenge in challenges: 
        if challenge in flags.get(name, {}): 
            FLAGS[name][challenge] += 1
            if FLAGS[name][challenge] > 2: 
                report.append(challenge)
        else: 
            FLAGS.setdefault(name, {})[challenge] = 1

    print(report)
    return report 

def alert_sentence(high_alert): 
    prompt = f"""
    The following mental health challenges have been demonstrated by the user more 3 or more times: {high_alert}. 
    Create a short one sentence statement to inform the user of their repeat behavior. 
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    # Return just the text content of the response 
    if response and hasattr(response, 'text'):
        return response.text
    return "We've noticed some recurring patterns in your entries that you might want to be aware of."

def journal_form_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        entry = request.POST.get('entry')

        #create nested dictionary -- name: challenge: number occuranced
        if name not in FLAGS: 
            FLAGS[name] = {} 
        
        # Call to functions to get generative AI response 
        challenge_description, coping_mechanisms = analyze_journal_entry(entry)
        local_recommendations = get_local_recommendations(location, coping_mechanisms)
        high_alert = check_flags(FLAGS, name, challenge_description)
        print(high_alert)

        if len(high_alert) >= 1: 
            challenge_description = alert_sentence(high_alert)
            print(f"challenge description: {challenge_description}")

        print(FLAGS)
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

    print(f"Retrieved from session: {challenge_description}, {coping_mechanisms}, {location}, {local_recommendations}")

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
