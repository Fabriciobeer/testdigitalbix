from django.db import models

# Create your models here.

class Empresa(models.Model):
    nome = models.CharField(max_length=255,default='')
    razao_social = models.CharField(max_length=255, default='')  
    ativa = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nome

class CNPJ(models.Model):
    empresa = models.ForeignKey(Empresa, related_name='cnpjs', on_delete = models.PROTECT)
    cnpj = models.CharField(unique=True, max_length=14, default = '')
    ativa = models.BooleanField(default=True)

    def __str__(self):

        return self.cnpj

class AreaEmpresa(models.Model):
    empresa = models.ForeignKey(Empresa, related_name='areas', on_delete = models.PROTECT)
    nome = models.CharField(max_length=255, default='')
    ativa = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('empresa', 'nome',)

    def __str__(self):

        return 'Área de ' + self.nome + ' da ' + self.empresa.nome

class Projeto(models.Model):
    empresa = models.ForeignKey(Empresa, related_name='projetos',on_delete = models.PROTECT)
    descricao = models.CharField(max_length=255,null=False)
    ativa = models.BooleanField(default=True)
    class Meta:
        unique_together = ('empresa', 'descricao',)