from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from .forms import CreateStoryForm


class HomeView(FormView):
    template_name = 'index.html'
    form_class = CreateStoryForm
    success_url = 'thanks/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        url = form.cleaned_data['url']
        profile = form.cleaned_data['profile']
        email = form.cleaned_data['email']
        form.create_story(url, profile, email)
        return super().form_valid(form)


class ThanksView(TemplateView):
    template_name = 'thanks.html'


class FAQView(TemplateView):
    template_name = 'faq.html'
