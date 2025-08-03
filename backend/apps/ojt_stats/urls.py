from django.urls import path
from .views import ojt_statistics_view, generate_ojt_statistics_view, export_detailed_ojt_data

urlpatterns = [
    path('ojt/', ojt_statistics_view, name='ojt_statistics'),
    path('generate/', generate_ojt_statistics_view, name='generate_ojt_statistics'),
    path('export-detailed/', export_detailed_ojt_data, name='export_detailed_ojt_data'),
] 