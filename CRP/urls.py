from django.urls import path
from . import views
#from django.conf import settings
#from django.views.static import serve

urlpatterns = [
    path('controle/', views.render_controle_page),
    #path('controle/inativos/', views.areas_cnpjs_inativos),
    path('controle/<str:acao>/', views.controle),
   	path('merge_empresas/', views.merge_empresas),
    path('', views.render_controle_page)
]