from django.urls import path
from .views import HomeView, ThanksView, get_args

app_name = 'ebook'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('thanks/', ThanksView.as_view(), name="thanks"),
    path('get/', get_args, name='get_args'),
]
