from django.db import models
from CRP.models import Empresa, CNPJ

class Nfe(models.Model):
    n_nfe = models.IntegerField(primary_key=True)
    empresa = models.ForeignKey(Empresa, on_delete = models.PROTECT)
    cnpj = models.ForeignKey(CNPJ, on_delete= models.PROTECT)
    data_emissao = models.DateField()
    data_fechamento = models.DateField()
    valor_total = models.DecimalField(max_digits=15 , decimal_places=2)
    description = models.TextField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['data_fechamento'])
        ]

    def __str__(self):
        return "Número da NFe {}".format(self.n_nfe)

class Parcela(models.Model):
    nfe = models.ForeignKey(Nfe, on_delete = models.PROTECT)
    data_esperada = models.DateField()
    valor_esperado = models.DecimalField(max_digits=15 , decimal_places=2)
    data_paga = models.DateField(null=True, blank=True)
    valor_pago = models.DecimalField(max_digits=15 , decimal_places=2, null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['data_esperada'])
        ]
    
    def __str__(self):
        return "Data esperada {0}, valor esperado {1}".format(self.data_esperada, self.valor_esperado)
     

class PadraoParcela(models.Model):
    cnpj = models.ForeignKey(CNPJ, on_delete = models.PROTECT)
    meses_pos_emissao = models.IntegerField()
    porcentual_a_pagar = models.FloatField()
    #projeto = models.TextField(max_length=45, null=True, blank=True)
    
    def __str__(self):
        return "Meses após emissão {0}, porcentual a pagar {1}".format(self.meses_pos_emissao, self.porcentual_a_pagar)

class Meta(models.Model):
    mes = models.DateField()
    valor = models.FloatField()
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return str(self.mes)
