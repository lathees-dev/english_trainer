from django import forms

class ResumeUploadForm(forms.Form):
    resume_image = forms.ImageField(label='Upload Resume Image', required=True)

class AnswerForm(forms.Form):
    answer = forms.CharField(label='Your Answer:', required=True)