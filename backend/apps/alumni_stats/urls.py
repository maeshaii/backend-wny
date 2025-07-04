from django.urls import path
from .views import alumni_statistics_view

urlpatterns = [
    path('alumni/', alumni_statistics_view, name='alumni_statistics'),
] 