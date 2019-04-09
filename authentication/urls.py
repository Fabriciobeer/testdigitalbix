from django.urls import path
from . import views
from django.views.generic import DetailView

urlpatterns = [
    path('logout/', views.userLogout),
    path('login/',views.userLogin),
    path('',views.userLogin),
    path('account/',views.account),
    path('rec_pass/', views.rec_pass)
]