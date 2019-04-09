from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from dateutil import parser
from .models import PadraoParcela, Parcela, Nfe, Meta
from CRP.models import Empresa, CNPJ
from authentication.views import validate_user_perm
from django.core.exceptions import PermissionDenied

@login_required(login_url='/auth/login?next=/FRP/')
def index(request):
    if validate_user_perm(request.user, financeiro=True):
        breadcrumb = [["/", "Home"], ["/FRP", "Financeiro"]]
        context = {"breadcrumb": breadcrumb}
        return render(request, 'FRP/index.html', context=context)
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")

@login_required(login_url='/auth/login?next=/FRP/nfes_abertas/')
def nfesAbertas(request):
    '''Renderiza a página de notas fiscais abertas'''

    if validate_user_perm(request.user, financeiro=True):
        breadcrumb = [["/", "Home"], ["/FRP", "Financeiro"], ["/FRP/nfes_abertas", "NF-e Abertas"]]
        parcelas_abertas = Parcela.objects.filter(valor_pago__isnull = True).order_by('data_esperada') 
        parcelas_fechadas = Parcela.objects.filter(valor_pago__isnull = False).order_by('data_paga') 
        context = {"breadcrumb":breadcrumb, "parcelas_abertas": parcelas_abertas, "parcelas_fechadas": parcelas_fechadas}
        return render(request, 'FRP/nfesAbertas.html', context=context)
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")

@login_required(login_url='/auth/login?next=/FRP/pagamento_padrao/')
def pagamentoPadrao(request):
    '''Renderiza a página de Pagamento Padrão'''
    if validate_user_perm(request.user, financeiro=True):
        empresas_cadastradas = Empresa.objects.all().order_by('nome')
        padroes_parcela = PadraoParcela.objects.all().order_by('meses_pos_emissao')
        breadcrumb = [["/", "Home"], ["/FRP", "Financeiro"], ["/FRP/pagamentoPadrao", "Pagamento Padrão"]]
        context = {"empresas":empresas_cadastradas, "breadcrumb":breadcrumb, "padroes":padroes_parcela}
        return render(request, 'FRP/pagamento_padrao.html', context=context)
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")

@login_required(login_url='/auth/login?next=/FRP/metas/')
def metas(request):
    '''Renderiza a página de Metas'''

    if validate_user_perm(request.user):
        metas = Meta.objects.all().order_by('-mes')
        breadcrumb = [["/", "Home"], ["/FRP", "Financeiro"], ["/FRP/metas", "Metas"]]
        context = {"metas":metas, "breadcrumb":breadcrumb}
        return render(request, 'FRP/metas.html', context=context)
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")

@login_required(login_url='/auth/login?next=/FRP/metas/')
def controle_metas(request, acao):
    '''Processa as operações de acordo com o valor da acao, podendo estas ser: Adicionar, Editar ou Deletar e redireciona para a página de renderização'''

    if validate_user_perm(request.user, financeiro=True):
        if request.method == 'POST':
            if acao == 'edit_meta':
                meta_id = int(request.POST['meta-id'])
                mes = parser.parse('01/'+request.POST['mes'], dayfirst=True)
                valor = float(request.POST['valor'].replace(",", "."))
                meta = Meta.objects.get(id=meta_id)
                meta.mes = mes
                meta.valor = valor
                meta.save()
                messages.success(request, 'Meta atualizada!')
        elif request.method == 'GET':
            if acao == 'remove_meta':
                meta_id = int(request.GET['pk'])
                meta = Meta.objects.get(id=meta_id)
                meta.delete()
                messages.error(request, 'Meta removida!')
            elif acao == 'new_meta':
                mes = parser.parse('01/'+request.GET['mes'], dayfirst=True)
                valor = float(request.GET['valor'].replace(",", "."))
                meta =  Meta(mes=mes, valor=valor).save()
                messages.success(request, 'Meta criada!')
    else:
        messages.error(request, 'Você não têm permissão para realizar esta operação!')

    return HttpResponseRedirect(reverse('metas'))

@login_required(login_url='/auth/login?next=/FRP/nfes_abertas/')    
def update_nfes(request, acao):
    '''Processa as operações de acordo com o valor da acao, podendo estas ser: Deletar ou Editar uma meta e redireciona para a página de renderização'''

    if validate_user_perm(request.user, financeiro=True):
        if request.method == 'POST':
            try:
                nfe_id = request.POST['n_nfe'][0]
                nfe = Nfe.objects.get(n_nfe=int(nfe_id))
                parcela = Parcela.objects.get(id=int(request.POST['parcela-id']))
                parcela.data_paga=parser.parse(request.POST['data_paga'], dayfirst=True)
                parcela.valor_pago=float(request.POST['valor_pago'].replace(",", "."))
                parcela.save()
            except ValueError:
                messages.info(request, 'Something went wrong :(')
        elif request.method == 'GET':
            if acao == "remove_nfes":
                Parcela.objects.filter(id=int(request.GET['pk'])).delete()
        return HttpResponseRedirect(reverse('nfesAbertas'))
    else:
        raise PermissionDenied("Você não possui permissão para realizar estas operações!")

@login_required(login_url='/auth/login?next=/FRP/pagamento_padrao/')
def controlePagamentoPadrao(request, acao):
    '''Processa as operações de acordo com o valor da acao, podendo estas ser: Adicionar ou Deletar Pagamento Padrão e redireciona para a página de renderização'''

    if validate_user_perm(request.user, financeiro=True):
        if request.method == 'POST':
            if acao == "addPagamentoPadrao":
                post_dict = transform_to_dict(request.POST)
                if bool(post_dict):
                    print(post_dict)
                    for padrao in range(len(post_dict['n_meses'])):
                        id_cnpj = int(post_dict['cnpj'][0])
                        meses = post_dict['n_meses'][padrao]
                        percentual = float(post_dict['percentual'][padrao].replace(",", "."))
                        cnpj = CNPJ.objects.get(id=id_cnpj)
                        try:
                            padrao_id = int(post_dict['padrao_id'][padrao])
                            pp = PadraoParcela(id=padrao_id, cnpj=cnpj, meses_pos_emissao=meses, porcentual_a_pagar=percentual)
                        except:
                            pp = PadraoParcela(cnpj=cnpj, meses_pos_emissao=meses, porcentual_a_pagar=percentual)
                        pp.save()
        elif request.method == 'GET':
            if acao == "deletaPadrao":
                PadraoParcela.objects.filter(id=int(request.GET['pk'])).delete()
        return HttpResponseRedirect(reverse('pagamentoPadrao'))
    else:
        raise PermissionDenied("Você não possui permissão para realizar estas operações!")

def transform_to_dict(queryDict):
    myDict = {}
    if len(list(queryDict)) > 1 :
        for key in list(queryDict):
            myDict[key] = queryDict.getlist(key)
    return myDict
    