from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pagamento_padrao/', views.pagamentoPadrao, name='pagamentoPadrao'),
    path('nfes_abertas/', views.nfesAbertas, name='nfesAbertas'),
    path('metas/', views.metas, name='metas'),
    path('metas/<str:acao>/', views.controle_metas),
    path('pagamento_padrao/<str:acao>/', views.controlePagamentoPadrao),
    path('nfes_abertas/<str:acao>/', views.update_nfes),
]