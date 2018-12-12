from django.urls import path

from .views import HomeView, ThanksView, FAQView

app_name = 'ebook'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('thanks/', ThanksView.as_view(), name="thanks"),
    path('faq/', FAQView.as_view(), name='faq')
]