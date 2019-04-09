from django.urls import path
from . import views
#from django.conf import settings
#from django.views.static import serve

urlpatterns = [
    path('', views.hrp_index),
    path('timesheet/submit_horario/', views.timesheet_submit_horario),
    path('timesheet/meus_registros/', views.timesheet_registros),
    path('timesheet/del_hora/', views.timesheet_del_hora),
    path('timesheet/edit_hora/', views.timesheet_edit_hora),
    path('timesheet/del_mass_horas/', views.timesheet_del_mass_horas),
    path('timesheet/generate_report/', views.generate_report),
    path('timesheet/', views.timesheet),
    path('allocation/add_allocation/', views.add_allocation),
    path('allocation/del_allocation/', views.del_allocation),
    path('allocation/', views.allocation),
    path('allocation/add_allocation/', views.add_allocation),
    path('allocation/', views.allocation),
    path('controle/', views.render_controle_page),
    path('controle/inativos/', views.colaboradores_inativos),
    path('controle/restaurar_colaborador/', views.render_controle_page_restaura_inativo),
    path('controle/<str:acao>/', views.controle),
    path('perfil/<str:pk>/', views.perfil),
    path('remover_ferias/<str:pk>/', views.del_ferias),
    path('add_ferias/<str:pk>/', views.add_ferias),
    path('change_profile_pic/<str:pk>/', views.profile_pic),
    path('download/', views.download),
    path('perfil/change_perm/<str:pk>/', views.change_perm),
    path('perfil/<str:acao>/<str:pk>/', views.editor_contrato)
]