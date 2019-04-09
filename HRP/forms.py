from django.forms import ModelForm, TextInput, TimeField, TimeInput, FileField
from .models import Colaborador

class AdmissaoForm(ModelForm):
	class Meta:
		model = Colaborador
		exclude = ['user']
		widgets = {
				'data_admissao': TextInput(attrs={'class':'datepicker','id':'data_admissao'}),
				'data_exp_carteira_trabalho' : TextInput(attrs={'class':'datepicker','id':'data_exp_carteira_trabalho'}),
				'data_nascimento': TextInput(attrs={'class':'datepicker','id':'data_nascimento'}),
				'data_cadastramento': TextInput(attrs={'class':'datepicker','id':'data_cadastramento'}),
				'data_exp_rg': TextInput(attrs={'class':'datepicker','id':'data_exp_rg'}),
				'horario_trab_i': TimeInput(attrs={'type':'time'}, format='%H:%M'),
				'horario_trab_f': TimeInput(attrs={'type':'time'}, format='%H:%M'),
				'horario_trab_intervalo': TimeInput(attrs={'type':'time'}, format='%H:%M')
		}