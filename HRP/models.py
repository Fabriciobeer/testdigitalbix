from django.db import models
from authentication.models import User
from CRP.models import AreaEmpresa, Projeto

CORES = (
    (1,'Branca'),
    (2,'Morena'),
    (3,'Amarela'),
    (4,'Parda'),
    (5,'Indígena')
    )

GENEROS = (
    ('M','Masculino'),
    ('F','Feminino'),
    ('O','Outro')
    )

class Colaborador(models.Model):
    nome = models.CharField(max_length=255, default='')
    email = models.EmailField(null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null = True)

    profile_pic = models.FileField(upload_to='profilePics/', default='profilePics/default.png')
    
    #DADOS ADMISSIONAIS
    #nome Empresa (sempre BIX)
    #nome (já contido nos dados padrão)
    nome_pai = models.CharField(max_length=255, default='')
    nome_mae = models.CharField(max_length=255, default='')
    #email (já contido nos dados padrão)
    telefone = models.CharField(max_length=255, default='')
    data_admissao = models.DateField(null=True)
    funcao = models.CharField(max_length=255, default='')
    escolaridade = models.CharField(max_length=255, default='')
    carteira_trabalho = models.CharField(max_length=255, default='')
    num_carteira_trabalho = models.CharField(max_length=255, default='')
    serie_carteira_trabalho = models.CharField(max_length=255, default='')
    data_exp_carteira_trabalho = models.DateField(null=True)
    municipio_nascimento = models.CharField(max_length=255, default='')
    uf_nascimento = models.CharField(max_length=255, default='')
    data_nascimento = models.DateField(null=True)
    endereco = models.CharField(max_length=255, default='')
    bairro = models.CharField(max_length=255, default='')
    cidade = models.CharField(max_length=255, default='')
    uf = models.CharField(max_length=255, default='')
    cep = models.CharField(max_length=255, default='')
    estado_civil = models.CharField(max_length=255, default='')
    cpf = models.CharField(max_length=255, default='')
    n_pis = models.CharField(max_length=255, default='')
    data_cadastramento = models.DateField(null=True)
    rg = models.CharField(max_length=255, default='')
    org_emissor_rg = models.CharField(max_length=255, default='')
    data_exp_rg = models.DateField(null=True)
    titulo_eleitor = models.CharField(max_length=255, default='')
    zona_titulo_eleitor = models.CharField(max_length=255, default='')
    secao_titulo_eleitor = models.CharField(max_length=255, default='')
    carteira_habilitacao = models.CharField(max_length=255, default='')
    num_carteira_reservista = models.CharField(max_length=255, default='')
    #dado no contrato
    #remuneracao = models.FloatField(null=True)
    #tipo_remuneracao = models.CharField(max_length=255, default='')
    horario_trab_i = models.TimeField(null=True)
    horario_trab_f = models.TimeField(null=True)
    horario_trab_intervalo = models.FloatField(null=True)
    vale_transporte = models.CharField(max_length=255, default='')
    raca_cor = models.IntegerField(choices=CORES, null=True)
    genero = models.CharField(choices=GENEROS, max_length=1, null=True)
    cpf_file = models.FileField(upload_to='docsAdmissionais/', null=True)
    id_file = models.FileField(upload_to='docsAdmissionais/', null=True)
    titulo_eleitor_file = models.FileField(upload_to='docsAdmissionais/', null=True)
    cart_reservista_file = models.FileField(upload_to='docsAdmissionais/', null=True)
    cert_nascimento_file = models.FileField(upload_to='docsAdmissionais/', null=True)
    comp_residencia_file = models.FileField(upload_to='docsAdmissionais/', null=True)
    cert_nascimento_filho_file = models.FileField(upload_to='docsAdmissionais/', null=True)
    
    def __str__(self):
        return self.nome

class Allocation(models.Model):
    resource = models.ForeignKey(Colaborador, on_delete=models.PROTECT)
    project = models.ForeignKey(Projeto, on_delete=models.PROTECT, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)


class ModeloContrato(models.Model):
    modalidade = models.CharField(max_length=255, null=False)
    carga_horaria = models.IntegerField(null=True)

    def __str__(self):
        return str(self.modalidade) + ' - ' + str(self.carga_horaria)

class Contrato(models.Model):
    colaborador = models.ForeignKey(Colaborador, on_delete=models.PROTECT)
    modelo = models.ForeignKey(ModeloContrato, on_delete=models.PROTECT, null=True)
    data_i = models.DateField(null=True)
    data_f = models.DateField(null=True)
    #módulo RH
    direito_ferias = models.IntegerField(default=30)
    remuneracao = models.FloatField(default=0)
    tipo_remuneracao = models.CharField(max_length=255, default='mensal')
    
    def __str__(self):
        return str(self.colaborador) + ' - ' + str(self.data_i)

    class Meta:
        indexes = [models.Index(fields=['-data_f'])]

class Ferias(models.Model):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    data_i = models.DateField(null=True)
    data_f = models.DateField(null=True)

    def __str__(self):
        return "Férias do {0} de {1} até {2}".format(self.contrato.colaborador.nome,self.data_i,self.data_f)

class HoraTrabalhada(models.Model):
    comentario = models.TextField(null=True)
    colaborador = models.ForeignKey(Colaborador, on_delete=models.PROTECT)
    area = models.ForeignKey(AreaEmpresa, on_delete=models.PROTECT)
    projeto = models.ForeignKey(Projeto, on_delete=models.PROTECT)
    hora = models.FloatField()
    data_execucao = models.DateField(null=True)
    data_preenchimento = models.DateField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['data_execucao'])
        ]

    def __str__(self):
        return "Horas: {0} / Data: {1} / Executor: {2}".format(self.hora, self.data_execucao, self.colaborador.nome)
