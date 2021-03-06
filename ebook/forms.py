from captcha.fields import ReCaptchaField
from django import forms

from .tasks import make_story


class CreateStoryForm(forms.Form):
    url = forms.URLField()
    email = forms.EmailField()
    captcha = ReCaptchaField()

    profile_choices = (
        ('kindle', 'Kindle 201..'),
        ('kindle_dx', 'Kindle DX'),
        ('kindle_fire', 'Kindle Fire'),
        ('kindle_oasis', 'Kindle Oasis 1,2'),
        ('kindle_pw', 'Kindle Paperwhite 1,2'),
        ('kindle_pw3', 'Kindle Paperwhite 3'),
        ('kindle_voyage', 'Kindle Voyage')
    )
    profile = forms.ChoiceField(widget=forms.Select,
                                choices=profile_choices)

    def create_story(self):
        url = self.cleaned_data['url']
        email = self.cleaned_data['email']
        profile = self.cleaned_data['profile']
        make_story.delay(url, profile, email)



