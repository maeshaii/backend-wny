from django.urls import path
from .views import alumni_list_view

urlpatterns = [
    path('alumni/', alumni_list_view, name='alumni_list'),
] 