from django import forms


#fields for the form 
class JournalForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    location = forms.CharField(max_length=100, required=True)
    entry = forms.CharField(widget=forms.Textarea, required=True)