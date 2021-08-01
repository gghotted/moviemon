from django.urls import path
from .views import TitleScreen


urlpatterns = [
    path('', TitleScreen.as_view(), name='title_screen')
]
