from django.urls import path
from .views import *


urlpatterns = [
    path('', TitleScreen.as_view(), name='title_screen'),
    path('worldmap', WorldMap.as_view(), name='worldmap'),
    path('battle/<str:moviemon_id>', Battle.as_view(), name='battle'),
    path('moviedex', Moviedex.as_view(), name='moviedex'),
    path('moviedex/<int:moviemon_id>', MoviedexDetail.as_view(), name='moviedex_detail'),
    path('options', Options.as_view(), name='options'),
    path('options/save_game', Save.as_view(), name='save'),
    path('options/load_game', Load.as_view(), name='load'),
]
