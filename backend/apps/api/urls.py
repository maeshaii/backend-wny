from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomTokenObtainPairView
from apps.alumni_users.views import alumni_list_view
from apps.shared.views import export_alumni_excel, import_alumni_excel, import_exported_alumni_excel

urlpatterns = [
    path('csrf/', views.get_csrf_token, name='get_csrf_token'),
    path('login/', views.login_view, name='login_view'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('import-alumni/', views.import_alumni_view, name='import_alumni'),
    path('alumni/statistics/', views.alumni_statistics_view, name='alumni_statistics'),
    path('alumni/list/', views.alumni_list_view, name='alumni_list'),
    path('alumni-list/', alumni_list_view, name='alumni_list_alias'),
    path('export-alumni/', export_alumni_excel, name='export_alumni_excel'),
    path('import-alumni/', import_alumni_excel, name='import_alumni_excel'),
    path('import-exported-alumni/', import_exported_alumni_excel, name='import_exported_alumni_excel'),
]
