from django.urls import path
from .views import LoginView, RegisterUserView, RegisterPhoneView, CompanyCarView, LocationView, StandardView, MessagesView, ReportView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('register1/', RegisterUserView.as_view(actions={'post': 'create'})),
    path('register2/', RegisterPhoneView.as_view(actions={'post': 'update'})),
    path('register_company/',
         CompanyCarView.as_view(actions={'post': 'create'})),
    path('company/messages/',
         MessagesView.as_view(actions={'get': 'list'})),
    path('location/', LocationView.as_view(actions={'post': 'create'})),
    path('company/standard/',
         StandardView.as_view(actions={'post': 'create', 'put': 'update', 'delete': 'destroy', 'patch': 'update'})),
    path('company/daily_reports/',
         ReportView.as_view(actions={'get': 'get_daily_reports'})),
    path('company/weekly_reports/',
         ReportView.as_view(actions={'get': 'get_weekly_reports'})),
    path('company/monthly_reports/',
         ReportView.as_view(actions={'get': 'get_monthly_reports'})),
]
