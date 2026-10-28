from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("signup/", views.signup, name="signup"),
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("trip/create/", views.create_trip, name="create_trip"),
    path("trip/<int:trip_id>/add-member/", views.add_member, name="add_member"),
    path("trip/<int:trip_id>/add-expense/", views.add_expense, name="add_expense"),
    path("trip/<int:trip_id>/report/", views.report, name="report"),
]
