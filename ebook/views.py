from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect

from .forms import CreateStoryForm
from .tasks import make_story


class HomeView(FormView):
    template_name = 'index.html'
    form_class = CreateStoryForm
    success_url = '/thanks/'


class ThanksView(TemplateView):
    template_name = 'thanks.html'


def get_args(request):
    form = CreateStoryForm(request.POST)
    if form.is_valid():
        url = form.cleaned_data['url']
        email = form.cleaned_data['email']
        profile = form.cleaned_data['profile']
        rs = make_story.delay(url, email, profile)
        rs.get(f)
    return HttpResponseRedirect('/thanks/')
