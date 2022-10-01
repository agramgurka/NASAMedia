from django.urls import path
from .views import SearchPage

urlpatterns = [
    path('', SearchPage.as_view()),
]