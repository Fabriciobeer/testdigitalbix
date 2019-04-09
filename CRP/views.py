from django.shortcuts import render
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.db import IntegrityError
from authentication.views import validate_user_perm
from django.http import HttpResponseRedirect
from .models import Empresa, AreaEmpresa, CNPJ, Projeto
from django.contrib.auth.decorators import login_required


@login_required(login_url='/auth/login?next=/CRP/areas/controle')
def controle(request, acao):
    '''Processa as operações de acordo com o valor da acao, podendo estas ser: adicionar, editar, inativar ou reativar e redireciona para a URL de renderização'''
    if validate_user_perm(request.user, executor=True, financeiro=True, RH=True):

        errorlog = None
        fontes = ['area','cnpj','empresa','projeto']

        if request.method == 'POST':
            if acao == 'add':
                errorlog = adicionar(request)
            elif acao == 'edit':
                errorlog = editar(request)
            else:
                raise SuspiciousOperation("Você está acessando um link pelo caminho indevido")    
        else:
            if acao == 'inativar':
                errorlog = inativar(request)
            elif acao == 'reativar':
                errorlog = reativar(request)

        if errorlog:
            if type(errorlog) == type(list()):
                return HttpResponseRedirect('/CRP/?confirmLog='+errorlog[1]+'?id='+str(errorlog[0])+'?fonte_r='+errorlog[2])
            elif errorlog in fontes:
                return HttpResponseRedirect('/CRP/?fonte='+errorlog+'#'+errorlog+"_h2")
            else:
                request.session['errorlog'] = errorlog
                return HttpResponseRedirect('/CRP/')
        else:
            return HttpResponseRedirect('/CRP/')
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página")


@login_required(login_url='/auth/login?next=/CRP/areas/controle')
def render_controle_page(request):
    '''Renderiza a página de controle de empresas'''

    if validate_user_perm(request.user, executor=True, financeiro=True, RH=True):

        if 'errorlog' in request.session.keys():
            errorlog = request.session.pop('errorlog')
        else:
            errorlog = None

        areas_empresas = AreaEmpresa.objects.filter(ativa=True,empresa__ativa=True).order_by('empresa__nome')
        empresas = Empresa.objects.filter(ativa=True).order_by('nome')
        cnpjs = CNPJ.objects.filter(ativa=True,empresa__ativa=True).order_by('empresa__nome')
        projetos = Projeto.objects.filter(ativa=True, empresa__ativa=True).order_by('empresa__nome')

        aux = areas_empresas.values('nome').distinct()
        areas_possiveis = list()
        for i in aux:
            areas_possiveis.append(i['nome'])

        breadcrumb = [
            ["/", "Home"],
            ["/CRP/", "Clientes"],
            ["/CRP/controle/", "Controle"]
            ]

        return render(request, 'CRP/controleAreas.html', {
            "areas_empresas": areas_empresas,
            "areas_possiveis": areas_possiveis,
            "empresas": empresas,
            "cnpjs": cnpjs,
            "breadcrumb": breadcrumb,
            "projetos": projetos,
            "errorlog": errorlog
            })
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta pagina")

@login_required(login_url='/auth/login?next=/CRP/areas/controle')
def merge_empresas(request):
    '''Atualiza todas as chaves estrangeiras que apontam para as empresas sendo mescladas, para o valor do id da primeira da lista de empresas selecionadas. 
    3Deleta todas os registros das empresas, menos o da primeira da lista de empresas selecionadas'''

    pk_list = list()
    if request.method == 'POST':
        for input_name in request.POST:
            if 'selected-' in input_name:
                aux = input_name.replace('selected-','')
                aux = int(aux)
                pk_list.append(aux)

        if len(pk_list) > 1:
            empresas = Empresa.objects.filter(pk__in=pk_list)
            merge_on = empresas[0]
            for empresa in empresas[1:]:
                areas = empresa.areas
                areas.update(empresa_id=merge_on.id)

                cnpjs = empresa.cnpjs
                cnpjs.update(empresa_id=merge_on.id)

                projetos = empresa.projetos
                projetos.update(empresa_id=merge_on.id)

                nfes = empresa.nfe_set
                nfes.update(empresa_id=merge_on.id)

                empresa.delete()

        return HttpResponseRedirect('/CRP/')
    else:
        SuspiciousOperation("Você está acessando um link pelo caminho indevido")    

def adicionar(request):
    '''Adiciona uma nova empresa, área ou cnpj caso não existam e retorna o que foi adicionado.
    Caso o objeto à ser adicionado já exista, o valor de retorno da função é um errolog'''

    # Verifica se está sendo adicionada uma nova empresa ou uma área/cnpj 
    if request.POST['empresa'] == 'outro':
        # nova empresa
        empresa = Empresa(nome=request.POST['outro'], razao_social=request.POST['razao_social'])
        empresa.save()
        fonte = 'empresa'
    else:
        empresa = Empresa.objects.get(id=request.POST['empresa'])
        try:
            if 'area-flag' in request.POST:
                # nova área
                AreaEmpresa(empresa=empresa, nome=request.POST['area']).save()
                fonte = 'area'
            elif 'cnpj-flag' in request.POST:
                # novo cnpj
                CNPJ(empresa=empresa, cnpj=request.POST['cnpj']).save()
                fonte = 'cnpj'
        except IntegrityError:
            if 'area-flag' in request.POST:
                area = AreaEmpresa.objects.get(empresa=empresa, nome=request.POST['area'])
                if area.ativa:
                    return "Esta combinação de Empresa e Área já existe."
                else:
                    return [area.id, "Esta combinação de Empresa e Área já existe e está inativa.\nConfirme se deseja reativá-la.", "area"]    
            elif 'cnpj-flag' in request.POST:
                cnpj = CNPJ.objects.get(empresa=empresa, cnpj=request.POST['cnpj'])
                if cnpj.ativa:
                    return "Este CNPJ já existe."
                else:
                    return [cnpj.id, "Este CNPJ já existe e está inativo.\nConfirme se deseja reativá-lo.", "cnpj"]
    return fonte


def editar(request):
    '''Edita o item identificado na URL e retorna o que foi adicionado. 
    Caso a atualização culmine em uma combinação existente, o valor de retorno da função é um errolog'''

    id = request.GET['pk']
    fonte = request.GET['fonte']

    try:
        if fonte == 'cnpj':
            cnpj = CNPJ.objects.get(id=id)
            flagN = False

            if request.POST['empresa'] != str(cnpj.empresa.id):
                #atualiza a chave estrangeira da empresa
                cnpj.empresa = Empresa.objects.get(id=request.POST['empresa'])
                flagN = True
            if request.POST['cnpj'] != cnpj.cnpj:
                #atualiza o valor do cnpj
                cnpj.cnpj = request.POST['cnpj']
                flagN = True
            if flagN:
                cnpj.save()
        elif fonte == 'area':
            area = AreaEmpresa.objects.get(id=id)
            

            if request.POST['empresa'] != str(area.empresa.id):
                #atualiza a chave estrangeira da empresa
                area.empresa = Empresa.objects.get(id=request.POST['empresa'])
                flagN = True
            if request.POST['area'] != area.nome:
                #atualiza a nome da área
                flagN = True
                nome = request.POST['area']
                area.nome = nome
            if flagN:
                area.save()
        elif fonte == 'empresa':
            empresa = Empresa.objects.get(id=id)

            flagN = False
            if request.POST['empresa'] != str(empresa.nome):
                empresa.nome = request.POST['empresa']
                flagN = True
            if request.POST['razao_social'] != str(empresa.razao_social):
                empresa.razao_social = request.POST['razao_social']
                flagN = True
            if flagN:
                empresa.save()
        elif fonte == 'projeto':
            projeto = Projeto.objects.get(id=id)

            flagN = False
            if request.POST['empresa'] != str(projeto.empresa.id):
                #atualiza a chave estrangeira da empresa
                projeto.empresa = Empresa.objects.get(id=request.POST['empresa'])
                flagN = True
            if request.POST['projeto'] != projeto.descricao:
                #atualiza a descrição do projeto
                flagN = True
                descricao = request.POST['projeto']
                projeto.descricao = descricao
            if flagN:
                projeto.save()

    except IntegrityError:
        return 'Esta combinação de Empresa + Área/CNPJ/Projeto já existe!'

    return fonte


def inativar(request):
    '''Desliga a flag "ativa" do item cujo tipo e id estão identificados na URL como parâmetros GET'''
    id = request.GET['pk']
    fonte = request.GET['fonte']

    try:

        if fonte == 'area':
            area = AreaEmpresa.objects.get(id=id)
            area.ativa = False
            area.save()
        elif fonte == 'cnpj':
            cnpj = CNPJ.objects.get(id=id)
            cnpj.ativa = False
            cnpj.save()
        elif fonte == 'empresa':
            empresa = Empresa.objects.get(id=id)
            empresa.ativa = False
            empresa.save()
        elif fonte == 'projeto':
            projeto = Projeto.objects.get(id=id)
            projeto.ativa = False
            projeto.save()
    except:
        return "Erro inativando " + fonte

    return fonte

def reativar(request):
    '''Seta a flag "ativa" do item cujo tipo e id estão identificados na URL como parâmetros GET'''

    id = request.GET['id']
    fonte = request.GET['fonte']

    try:

        if fonte == 'area':
            area = AreaEmpresa.objects.get(id=id)
            area.ativa = True
            area.save()
        elif fonte == 'cnpj':
            cnpj = CNPJ.objects.get(id=id)
            cnpj.ativa = True
            cnpj.save()
        elif fonte == 'empresa':
            empresa = Empresa.objects.get(id=id)
            empresa.ativa = True
            empresa.save()
        elif fonte == 'projeto':
            projeto = Projeto.objects.get(id=id)
            projeto.ativa = True
            projeto.save()
    except:
        return "Erro ativando " + fonte

    return fonte