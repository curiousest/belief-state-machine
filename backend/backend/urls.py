# backend/urls.py
from django.urls import path
from api.views import ExtractBeliefsView, GenerateParableView

urlpatterns = [
    path('extract_beliefs/', ExtractBeliefsView.as_view(), name='extract_beliefs'),
    path('generate_parable/', GenerateParableView.as_view(), name='generate_parable'),
]
