from django.urls import path
from .views import TitleScreen


urlpatterns = [
    path('', TitleScreen.as_view(), name='title_screen'),
    # path('worldmap', [...], name='worldmap'),
    # path('battle/<int:moviemon_id>', [...], name='battle'),
    # path('moviedex', [...], name='moviedex'),
    # path('moviedex/<int:moviemon_id>', [...], name='moviedex_detail'),
    # path('options', [...], name='options'),
    # path('options/save_game', [...], name='save'),
    # path('options/load_game', [...], name='load'),
]
