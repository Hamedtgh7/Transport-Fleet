from django.urls import path
from .views import LoginView, RegisterUserView, RegisterPhoneView, CompanyCarView, LocationView, StandardView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('register1/', RegisterUserView.as_view(actions={'post': 'create'})),
    path('register2/', RegisterPhoneView.as_view(actions={'post': 'update'})),
    path('register_company/',
         CompanyCarView.as_view(actions={'post': 'create'})),
    path('location/', LocationView.as_view(actions={'post': 'create'})),
    path('standard/', StandardView.as_view(
        actions={'post': 'create', 'put': 'update', 'delete': 'destroy'}))
]
