from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .models import Colaborador, Contrato, HoraTrabalhada, ModeloContrato, Allocation, Ferias
from CRP.models import AreaEmpresa, Empresa, Projeto
from django.contrib.auth.decorators import login_required
from authentication.views import userRegister, validate_user_perm, random_password_generator
from authentication.models import User
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.utils.datastructures import MultiValueDictKeyError
import datetime
from django.conf import settings
from django.core.mail import send_mail
from json import loads, dumps
from django.conf import settings
from django.db import IntegrityError
from .forms import AdmissaoForm
from re import compile
import os
from django.conf import settings
from django.http import HttpResponse
from math import ceil

@login_required(login_url='/auth/login?next=/HRP/')
def hrp_index(request):
    
    breadcrumb = [["/","Home"],["/HRP/","RH"]]

    return render(request, 'HRP/indexHRP.html', {"breadcrumb": breadcrumb})

@login_required(login_url='/auth/login?next=/HRP/timesheet/')
def timesheet(request):
    '''View que renderiza a página da timesheet'''

    if validate_user_perm(request.user):
        empresas = Empresa.objects.all().order_by('nome')

        empresas_list = list()
        areas_dict = dict()
        projetos_dict = dict()
        for empresa in empresas:
            empresas_list.append((empresa.nome, empresa.id))

            #Esses dicionários têm como chave o id da empresa e como valor suas respectivas áreas/projetos
            areas_dict[empresa.id] = empresa.areas.filter(ativa=True).order_by('nome')
            projetos_dict[empresa.id] = empresa.projetos.filter(ativa=True).order_by('descricao')

        breadcrumb = [["/", "Home"], ["/HRP/", "RH"], 
                      ["/HRP/timesheet/", "Timesheet"]]

        return render(request, 'HRP/timesheet.html', {'empresas':empresas_list, "areas":areas_dict, 'projetos': projetos_dict, "breadcrumb": breadcrumb})
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")

@login_required(login_url='/auth/login?next=/HRP/timesheet/')
def timesheet_registros(request):
    '''View que renderiza a página de registros da timesheet'''
    if validate_user_perm(request.user):
        
        #timedelta armazena o valor do formulário 'apartir de:', por padrão é 30.
        if request.method == 'POST':
            if 'filtro_data' in request.POST:
                timedelta = int(request.POST['filtro_data'])
            else:
                timedelta = 30
        else:
            if 'timedelta' in request.GET:
                timedelta = int(request.GET['timedelta'])
            else:
                timedelta = 30

        if timedelta != 0:
            filtro_data = datetime.date.today() - datetime.timedelta(days = timedelta)        
            horas_registradas = HoraTrabalhada.objects.filter(colaborador = request.user.colaborador,data_execucao__gte = filtro_data).order_by('-data_execucao')
        else:#todas
            horas_registradas = HoraTrabalhada.objects.filter(colaborador = request.user.colaborador).order_by('-data_execucao')


        empresas = Empresa.objects.all()

        empresas_list = list()
        #Esses dicionários têm como chave o id da empresa e como valor suas respectivas áreas/projetos
        areas_dict = dict()
        projetos_dict = dict()
        for empresa in empresas:
            empresas_list.append((empresa.nome, empresa.id))
            areas_dict[empresa.id] = empresa.areas.filter(ativa=True).order_by('nome')
            projetos_dict[empresa.id] = empresa.projetos.filter(ativa=True).order_by('descricao')

        breadcrumb = [["/","Home"],["/HRP/","RH"],["/HRP/timesheet/", "Timesheet"],["/HRP/timesheet/meus_registros", "Registros"] ]

        return render(request, 'HRP/timesheet_registros.html', {'horas_registradas':horas_registradas, 'empresas':empresas_list, "areas":areas_dict, 'projetos': projetos_dict, "timedelta":timedelta, "breadcrumb": breadcrumb})
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")

@login_required(login_url='/auth/login?next=/HRP/timesheet/')
def timesheet_del_hora(request):
    '''View que deleta a hora trabalhada do usuário logado, cujo id se encontra como parâmetro na URL e redireciona para a URL de renderização'''

    if validate_user_perm(request.user):
        timedelta = '30'
        if request.method == 'GET' and 'pk' in request.GET:
            id = int(request.GET['pk'])
            try:
                timedelta = request.GET['timedelta']
            except:
                pass
            
            try:
                hora = HoraTrabalhada.objects.get(id=id, colaborador_id = request.user.colaborador.id)
            except HoraTrabalhada.DoesNotExist:
                raise PermissionDenied("Você não possui permissão para realizar esta operação!")
            else:
                hora.delete()

        return HttpResponseRedirect('/HRP/timesheet/meus_registros/?timedelta='+timedelta)
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")

@login_required(login_url='/auth/login?next=/HRP/timesheet/')
def timesheet_edit_hora(request):
    '''View que edita a hora trabalhada, cujo id se encontra como parâmetro na URL e as novas informações no POST e redireciona para a URL de renderização'''

    if validate_user_perm(request.user):
        timedelta = '30'

        log_erro = 'Erro desconhecido'

        if request.method == 'POST' and 'pk' in request.GET:
            id = int(request.GET['pk'])
            try:
                timedelta = request.GET['timedelta']
            except:
                pass
        
            # ------------ CTRL+C - CTRL+V submit_horario --------
            try:
                horario = HoraTrabalhada.objects.get(id=id, colaborador_id = request.user.colaborador.id)
            except HoraTrabalhada.DoesNotExist:
                raise PermissionDenied("Você não possui permissão para realizar esta operação!")
            else:
                try:
                    # Getting the POST request
                    post = request.POST   
                    comentario = post['comentario']
                    id_projeto = post['projeto']
                    id_area = post['area']
                    horas = '0' + post['horas']

                    
                except:
                    log_erro = "Erro na estrutura do request HTTP"
                else:
                    try:
                        # Manipulating the POST request data
                        area = AreaEmpresa.objects.get(id=id_area)
                        projeto = Projeto.objects.get(id=id_projeto)
                        hora = float(horas)
                    except:
                        log_erro = "Erro nos dados do POST"   
                    else:
                        try:
                            # Inserting values into the database
                            horario.comentario = comentario
                            horario.area = area
                            horario.projeto = projeto
                            horario.hora = hora
                            horario.save()
                        except:
                            log_erro = "Erro inserindo os dados no banco de dados"
                        else:
                            log_erro = "Operação completada com sucesso"

            # ----------------------------------------------------------------


        return HttpResponseRedirect('/HRP/timesheet/meus_registros/?timedelta='+timedelta+'&log_erro='+log_erro)
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")

@login_required(login_url='/auth/login?next=/HRP/timesheet/')
def timesheet_del_mass_horas(request):
    '''View que deleta as horas trabalhadas selecionadas no registro do usuário logado e redireciona para a URL de renderização'''

    if validate_user_perm(request.user):
        timedelta = '30'
        if request.method == 'POST':
            try:
                timedelta = request.GET['timedelta']
            except:
                pass
            
            #um checkbox não selecionado não se encontra nos dados do POST.
            pk_list = list()
            for input_name in request.POST:
                if 'selected-' in input_name:
                    aux = input_name.replace('selected-','')
                    aux = int(aux)
                    pk_list.append(aux)

            HoraTrabalhada.objects.filter(pk__in=pk_list, colaborador_id = request.user.colaborador.id).delete()

        return HttpResponseRedirect('/HRP/timesheet/meus_registros/?timedelta='+timedelta)
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")

@login_required(login_url='/auth/login?next=/HRP/timesheet/')
def timesheet_submit_horario(request):
    '''View que processa o request AJAX e registra uma hora trabalhada com os dados do POST para o usuário logado. Retorna sucesso ou falha + log para o JavaScript'''

    if validate_user_perm(request.user):
        if request.method == 'POST':
            response_data = {}
            status_ok = False
            log_erro = 'Erro desconhecido'

            try:
                # Getting the POST request data
                post = request.POST
                datas = post['datas']
                comentario = post['comentario']
                projeto = post['projeto']
                novo_projeto = post['novo_projeto']
                id_area = post['area']
                horas = '0' + post['horas']
                minutos = '0' + post['minutos']
            except:
                status_ok = False
                log_erro = "Erro na estrutura do request HTTP"
            else:
                try:
                    # Manipulating the POST request data
                    area = AreaEmpresa.objects.get(id=id_area)
                    # Verifica se adiciona um novo projeto
                    if projeto == 'outro':
                        try:
                            projeto = Projeto(descricao=novo_projeto, empresa=area.empresa)
                            projeto.save()
                            response_data['projeto'] = [projeto.empresa.id,projeto.descricao,projeto.id]
                        except IntegrityError:
                            # O projeto sendo adicionado já existe, sendo assim, um projeto não é adicionado e é usado o que já existe.
                            response_data['projeto'] = False
                            projeto = Projeto.objects.get(descricao=novo_projeto, empresa=area.empresa)    
                    else:
                        projeto = Projeto.objects.get(id=projeto)

                    datas = list(map(lambda x: datetime.datetime.strptime(x, "%m/%d/%Y"), datas.split(',')))
                    hora = (int(horas) + (int(minutos)/60))/len(datas)
                    data_preenchimento = datetime.date.today()
                except:
                    status_ok = False
                    log_erro = "Erro nos dados do POST"
                else:
                    try:
                        # Inserting values into the database
                        for data_execucao in datas:
                            horario = HoraTrabalhada(comentario=comentario, 
                                                     colaborador=request.user.colaborador,
                                                     area=area,
                                                     projeto=projeto,
                                                     data_execucao=data_execucao,
                                                     data_preenchimento=data_preenchimento,
                                                     hora=hora)
                            horario.save()
                    except:
                        status_ok = False
                        log_erro = "Erro inserindo os dados no banco de dados"
                    else:
                        status_ok = True
                        datas = list(map(lambda x: x.strftime("%d/%m/%y"), datas))
                        minutos = ceil((hora % 1)*60)
                        horas = int(hora)
                        valores_inseridos = {"Dias": datas, "Tempo por dia": str(horas) + "h" + str(minutos), "Área": area.nome + " da " + area.empresa.nome}

            
            response_data['status'] = status_ok

            if status_ok:
                response_data['valores_inseridos'] = valores_inseridos
            else:
                response_data['log_erro'] = log_erro

            return HttpResponse(
                dumps(response_data),
                content_type="application/json"
            )
        else:
            return HttpResponse(
                dumps({"status": False, "log_erro": "POST inexistente no request"}),
                content_type="application/json"
            )
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")

@login_required(login_url='/auth/login?next=/HRP/controle/')
def generate_report(request):
    from djqscsv import render_to_csv_response
    if validate_user_perm(request.user):
        timedelta = '30'
        if request.method == 'POST':
            try:
                timedelta = request.GET['timedelta']
            except:
                pass
            
            #um checkbox não selecionado não se encontra nos dados do POST.
            pk_list = list()
            for input_name in request.POST:
                if 'selected-' in input_name:
                    aux = input_name.replace('selected-','')
                    aux = int(aux)
                    pk_list.append(aux)

            if len(pk_list) == 0:
                if 'timedelta' in request.GET:
                    timedelta = int(request.GET['timedelta'])
                else:
                    timedelta = 30
                filtro_data = datetime.date.today() - datetime.timedelta(days = timedelta)        
                horas_trabalhadas = HoraTrabalhada.objects.filter(colaborador = request.user.colaborador,data_execucao__gte = filtro_data)
            else:
                horas_trabalhadas = HoraTrabalhada.objects.filter(pk__in=pk_list, colaborador_id = request.user.colaborador.id)
            horas_trabalhadas = horas_trabalhadas.values('id','colaborador__nome','area__empresa__nome','area__nome','projeto__descricao','comentario','hora','data_execucao','data_preenchimento')
            horas_trabalhadas = render_to_csv_response(horas_trabalhadas, delimiter=";")

            response = HttpResponse(horas_trabalhadas, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename="registro_horas.csv"'
            return response
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")


# ------------------------- CONTROLE E CADASTRO DE COLABORADRES ----------------------------------

@login_required(login_url='/auth/login?next=/HRP/controle/')
def controle(request, acao):
    '''Processa as operações de acordo com o valor da acao, podendo estas ser: adicionar colaborador, editar contrato e inativar ou reativar colaborador e redireciona para a página de renderização'''

    if validate_user_perm(request.user, RH=True):
        try:
            errorlog = ""
            if (request.method == 'POST'):
                if acao == 'add_colab':
                    try:
                        adicionar_colaborador(request)
                    except Exception as e:
                        errorlog = e.args[1]
                    else:
                        errorlog = "Colaborador adicionado com sucesso!"
                elif acao == 'edit_contrato':
                    edit_contrato(request)
                elif acao == 'restaura_contrato':
                    restaura_contrato(request)
                else:
                    raise SuspiciousOperation("Você está acessando um link por um caminho indevido.")    
            else:
                if acao == 'finalizar_contrato':
                    finaliza_contrato(request)
        except Exception as e:
            errorlog = e.args[1]
        
        request.session['errorlog'] = errorlog
        return HttpResponseRedirect('/HRP/controle/')
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")

@login_required(login_url='/auth/login?next=/HRP/controle/')
def render_controle_page(request):
    '''Renderiza a página de colaboradores ativos'''
    if validate_user_perm(request.user, RH=True):

        if 'errorlog' in request.session.keys():
            errorlog = request.session.pop('errorlog')
        
        
        contratos = Contrato.objects.filter(data_f__isnull=True).order_by('colaborador__nome')
        modelo_contratos = ModeloContrato.objects.all()

        breadcrumb = [["/", "Home"], ["/HRP/", "RH"], 
                      ["/HRP/controle/", "Colaboradores"]]

        return render(request, 'HRP/controleColabs.html', {
            "contratos": contratos,
            "modelo_contratos": modelo_contratos,
            "breadcrumb": breadcrumb,
            "errorlog": errorlog})
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")

@login_required(login_url='/auth/login?next=/HRP/inativos/')
def colaboradores_inativos(request, RH=True):
    '''Renderiza a página de colaboradores inativos'''
    if validate_user_perm(request.user, executor=True):
        
        colaboradores = Colaborador.objects.exclude(contrato__data_f=None)

        breadcrumb = [["/","Home"],["/HRP/","RH"],["/HRP/controle/", "Colaboradores"],["/HRP/controle/inativos/", "Inativos"]]

        return render(request, 'HRP/colabInativos.html',{"colaboradores_inativos":colaboradores, "breadcrumb": breadcrumb})

    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")

@login_required(login_url='/auth/login?next=/HRP/inativos/')
def render_controle_page_restaura_inativo(request, RH=True):
    '''Renderiza a página de colaboradores ativos, com o colaborador à ser reativado'''

    if validate_user_perm(request.user, executor=True):
        colab_readmitido = request.GET['pk']
        
        contratos = Contrato.objects.filter(data_f__isnull=True).order_by('colaborador__nome')
        modelo_contratos = ModeloContrato.objects.all()

        colab_readmitido = Contrato.objects.filter(colaborador_id =  colab_readmitido).order_by('-data_f')[0]

        breadcrumb = [["/","Home"],["/HRP/","RH"],["/HRP/controle/", "Colaboradores"]]
        
        return render(request, 'HRP/controleColabs.html', {
            "contratos": contratos,
            "modelo_contratos": modelo_contratos,
            "colab_readmitido":colab_readmitido,
            "breadcrumb": breadcrumb
            })
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")

def new_user_email(colaborador,password):
    '''Envia e-mail de confirmação de criação de usuário contendo as credênciais de acesso'''
    mail_subject = 'Usuário na intrabix criado com sucesso'
    mail_content = 'Seu usuário na intrabix foi criado com sucesso!\nlogin: '+ colaborador.user.username + '\nsenha: ' + password
    destinatarios = [colaborador.email]
    send_mail(mail_subject, mail_content, settings.EMAIL_SENDER, destinatarios, fail_silently=False)

def finaliza_contrato(request):
    '''Seta a data de termino do contrato com id igual ao parâmetro pk no GET para o dia de hoje'''
    contrato = Contrato.objects.get(id=request.GET['pk'])
    #Deixa o colaborador como um usuário inativo
    contrato.colaborador.user.is_active = False
    contrato.colaborador.user.save()
    if contrato.data_f is None: #Contrato está vigente
        #finaliza o contrato ao adicionar uma data de termino
        contrato.data_f = datetime.date.today()
        contrato.save()

def edit_contrato(request):
    '''Altera o nome do colaborador e caso exista alguma alteração no contrato, chama a função finaliza_contrato e cria um novo contrato com data de início igual a hoje, com as informações contidas no POST'''
    contrato = Contrato.objects.get(id=request.GET['pk'])
    if request.POST['nome'] != contrato.colaborador.nome:
        #Altera o nome do colaborador
        contrato.colaborador.nome = request.POST['nome']
        contrato.colaborador.save()

    if request.POST['modelo-contrato'] != str(contrato.modelo.id):
        modelo = ModeloContrato.objects.get(id=request.POST['modelo-contrato'])

        finaliza_contrato(request)
        contrato = Contrato(colaborador=contrato.colaborador, modelo=modelo, data_i=datetime.date.today())
        contrato.save()
        #Deixa o colaborador como um usuário ativo, uma vez que a função finaliza_contrato deixa o colaborador como um usuário inativo
        contrato.colaborador.user.is_active = True
        contrato.colaborador.user.save()
    else:
        return
    
    return contrato        

def restaura_contrato(request):
    '''Seta a flag de ativo do colaborador e cria um novo contrato'''
    contrato = Contrato.objects.get(id=request.GET['pk'])

    contrato.colaborador.user.is_active = True
    contrato.colaborador.user.save()
    if request.POST['nome'] != contrato.colaborador.nome:
        
        contrato.colaborador.nome = request.POST['nome']
        contrato.colaborador.save()
        
    if request.POST['modelo-contrato'] != str(contrato.modelo.id):
        modelo = ModeloContrato.objects.get(id=request.POST['modelo-contrato'])
    else:
        modelo = contrato.modelo    
    
    contrato = Contrato(colaborador=contrato.colaborador, modelo=modelo, data_i=datetime.date.today())
    contrato.save()  

def adicionar_colaborador(request):
    '''Adiciona um colaborador, cria um usuário e um contrato para este colaborador e retorna o colaborador adicionado'''
    colaborador = Colaborador(nome=request.POST['nome'], email=request.POST['email'])
    #definição de credênciais de acesso do usuário
    username = username_generator(colaborador)
    password = random_password_generator()   
    
    #Define as permissões (obs: checkboxes só são incluidas nos dados do POST quando setadas como verdadeiro)
    is_manager = 'is_manager' in request.POST
    is_RH = 'is_RH' in request.POST
    is_financeiro = 'is_financeiro' in request.POST
    is_executor = 'is_executor' in request.POST

    #Definição do nome de usuário
    while True:

        try:
            # Verifica se o e-mail está disponível
            Colaborador.objects.get(email=colaborador.email)
        except Colaborador.DoesNotExist:
            try:
                # Verifica se o nome de usuário está disponível
                User.objects.get(username=username)
            except User.DoesNotExist: 
                # Cria um usuário, já que o username é valido
                user = userRegister(username=username, password=password, is_executor=is_executor, is_manager=is_manager, is_financeiro=is_financeiro, is_RH=is_RH)
                break
            else:
                # Nome de usuário já cadastrado, gera um usuário aleatório 
                username=random_password_generator()
        else:
            raise Exception("E-mail em uso", "Este e-mail já está em uso por outro colaborador.")

    colaborador.user = user
    colaborador.save()

    # Envia o email com as credências de acesso
    try:
        new_user_email(colaborador,password)
    except:
        pass
    

    modelo = ModeloContrato.objects.get(id=request.POST['modelo-contrato'])
    Contrato(colaborador=colaborador, modelo=modelo, data_i=datetime.date.today()).save()
    return colaborador
    
def username_generator(colaborador):

    return colaborador.email

# --------------------------------- PERFIL ------------------------------------------------
@login_required(login_url='/auth/login?next=/HRP/')
def perfil(request, pk):
    ''' Renderiza a página de perfil e processa a submissão da form de dados admissionais se o método do request for = POST'''
    if validate_user_perm(request.user, RH=True) or request.user.colaborador.id == int(pk):
        
        #src é a variável que representa qual aba de dados estava selecionada, pode ser 'dados' ou 'adm'
        src = request.GET.get('src')
        errorlog = request.GET.get('errorlog')

        try:
            colaborador = Colaborador.objects.get(id=pk)
        except Colaborador.DoesNotExist:
            raise SuspiciousOperation("Você está acessando um link por um caminho indevido.")        

        # Esta flag armazena o estado do formulário, se este foi ou não aceito e validado. Caso o formulário não seja aceito, uma nova instância de formulário não será criada, ...continua
        # mas será retornada a instância, sem salvá-la, contendo os dados já preenchidos. 
        flag = True
        if request.method == 'POST':
            src = 'adm'
            #Instância um objeto de Formulário, referenciando o colaborador do perfil, com os dados do request.POST
            admissao = AdmissaoForm(request.POST, request.FILES,  instance=colaborador)
            
            # CAMPOS OBRIGATÓRIOS
            required = ['nome','email']
            # REGEX para identificação de datas
            date_pattern = compile("[0-3][0-9]\/[01][0-9]\/[0-9][0-9][0-9][0-9]$")
            
            # Para cumprir requisitos de CSS, os campos não obrigatórios foram setados como obrigatório. Desta forma, este for ...continue
            # seta todos os campos não contidos no required como NÃO OBRIGATÓRIOS.

            #Também são adaptados os formatos da data para o aceito pelo python.
            for key,val in admissao.fields.items():
                if key not in required:
                    val.required = False
                try:
                    if date_pattern.match(request.POST[key]):
                    # é uma data
                        if not request.POST._mutable:
                           # permite alteração do dado do POST
                           request.POST._mutable = True
                        # altera o dado do POST para um formato aceito pelo Model
                        request.POST[key] = datetime.datetime.strptime(request.POST[key], "%d/%m/%Y")
                except MultiValueDictKeyError:
                    pass

            if request.POST._mutable:
                request.POST._mutable = False

            # Verifica se o formulário é válido
            if admissao.is_valid():
                errorlog = "Dados salvos com sucesso!"
                admissao.save(commit=True)
            else:
                errorlog = "Dados invalidos. O formulário não foi salvo"

                # Define o formulário que será renderizado para o usuário como o formulário com erros que foi submetido
                for key,val in admissao.fields.items():
                    if key not in required:
                        val.required = True
                
                adm_form = admissao
                flag = False

        # Só instanciará um novo formulário caso não hajam falhas na submissão do formulário, caso contrário o formulário que será ...continua
        # renderizado para o usuário foi definido como o formulário com erros que foi submetido 
        if flag:
            adm_form = AdmissaoForm(instance=colaborador)                
        
        contratos = Contrato.objects.filter(colaborador = colaborador)
        ferias = Ferias.objects.filter(contrato__colaborador=colaborador)
        
        # Soma o saldo de ferias de cada contrato do colaborador, resultando no saldo positivo final
        saldo_ferias = 0
        for contrato in contratos:
            if contrato.data_f is None:
                saldo_ferias += (datetime.date.today() - contrato.data_i).days * (contrato.direito_ferias/365)
            else:
                saldo_ferias += (contrato.data_f - contrato.data_i).days * (contrato.direito_ferias/365)
               
        ferias_list = list()
        # Subtrai o valor de dias de férias registrado, do saldo positivo final, resultando no saldo final
        for registro in ferias:
            aux = (registro.data_f - registro.data_i).days
            saldo_ferias -= aux

            ferias_list.append([aux, registro.data_i.strftime("%d/%m/%y") + ' - ' + registro.data_f.strftime("%d/%m/%y"), registro.id])

        saldo_ferias = int(saldo_ferias)

        if request.user.is_RH or request.user.is_manager:
            modelo_contratos = ModeloContrato.objects.all()
        else:
            modelo_contratos = None
        
        breadcrumb = [["/","Home"],["/HRP/","RH"],["/HRP/controle","Colaboradores"],["/HRP/perfil","Perfil"]]
        if request.user.is_RH or request.user.is_manager:
             return render(request, 'HRP/profile.html', {"breadcrumb": breadcrumb, "pk":pk, "media_url":settings.MEDIA_URL, "saldo_ferias":saldo_ferias,"adm_form":adm_form, "ferias":ferias_list,"errorlog":errorlog,"src":src, "contratos":contratos,"modelo_contratos":modelo_contratos, "user":colaborador.user})
        else:
            return render(request, 'HRP/profile.html', {"breadcrumb": breadcrumb, "pk":pk, "media_url":settings.MEDIA_URL, "saldo_ferias":saldo_ferias,"adm_form":adm_form, "ferias":ferias_list,"errorlog":errorlog,"src":src})
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")
       
@login_required(login_url='/auth/login?next=/HRP/')
def del_ferias(request, pk):
    '''Deleta o período de férias especificado no <str:pk> e redireciona para a página de renderização de perfil'''

    ferias = Ferias.objects.get(id=pk)
    colab_id = ferias.contrato.colaborador_id
    if validate_user_perm(request.user, RH=True) or request.user.colaborador.id == colab_id: 
        ferias.delete()

        return HttpResponseRedirect('/HRP/perfil/' + str(colab_id))
    else:
        raise PermissionDenied("Você não possui permissão para realizar esta operação!")

@login_required(login_url='/auth/login?next=/HRP/')
def add_ferias(request, pk):
    '''Adiciona o período de férias especificado no <str:pk>, conforme os dados do POST e redireciona para a página de renderização de perfil'''

    if validate_user_perm(request.user, RH=True) or request.user.colaborador.id == int(pk): 
        data_i = datetime.datetime.strptime(request.POST['data_i'], "%d/%m/%Y")
        data_f = datetime.datetime.strptime(request.POST['data_f'], "%d/%m/%Y")
        try:
            contrato = Contrato.objects.get(colaborador_id=pk, data_f__isnull=True)
        except Contrato.DoesNotExist:
            raise SuspiciousOperation("Este colaborador não possui um contrato ativo, você está acessando este link por um caminho indevido.")    
        else:
            Ferias(data_i=data_i, data_f=data_f, contrato=contrato).save()

        return HttpResponseRedirect('/HRP/perfil/' + pk)
    else:
        raise PermissionDenied("Você não possui permissão para realizar esta operação!")

@login_required(login_url='/auth/login?next=/HRP/')
def profile_pic(request, pk):
    '''Atualiza a foto de perfil do colaborador especificado no <str:pk>'''
    if validate_user_perm(request.user, RH=True) or request.user.colaborador.id == int(pk): 
        pic = request.FILES['profile-pic']
        colaborador = Colaborador.objects.get(id=pk)
        colaborador.profile_pic = pic
        colaborador.save()

        return HttpResponseRedirect('/HRP/perfil/' + pk)
    else:
        raise PermissionDenied("Você não possui permissão para realizar esta operação!")

@login_required(login_url='/auth/login?next=/HRP/')
def change_perm(request, pk):
    '''Atualiza as permissões de usuário do colaborador especificado no <str:pk>'''
    if validate_user_perm(request.user, RH=True):
        user = Colaborador.objects.get(id=pk).user
        user.is_manager = 'is_manager' in request.POST
        user.is_RH = 'is_RH' in request.POST
        user.is_financeiro = 'is_financeiro' in request.POST
        user.is_executor = 'is_executor' in request.POST
        user.save()
        return HttpResponseRedirect('/HRP/perfil/' + pk + "/?src=dados")
    else:
        raise PermissionDenied("Você não possui permissão para realizar esta operação!")

@login_required(login_url='/auth/login?next=/HRP/')
def editor_contrato(request, acao, pk):
    '''Processa as operações deletar e editar, confrome a <str:acao> do contrato com id = <str:pk>'''
    if validate_user_perm(request.user, RH=True):
        errorlog = ""
        if acao == 'del_contrato':
            ctr = Contrato.objects.get(id=pk)
            colab_id = ctr.colaborador_id
            ctr.delete()
        elif acao == 'edit_contrato':
            if request.method == 'POST':
                ctr = Contrato.objects.get(id=pk)
                colab_id = ctr.colaborador_id
                #Regex para processar datas 
                date_pattern = compile("[0-3][0-9]\/[01][0-9]\/[0-9][0-9][0-9][0-9]$")

                data_i = request.POST['data_i']
                data_f = request.POST['data_f']
                remuneracao = request.POST['remuneracao']
                tipo_remuneracao = request.POST['tipo_remuneracao']
                modelo = request.POST['modelo-contrato']
                ferias = request.POST['ferias']
                
                # Atualiza o valor da data_i se esta for valida
                if date_pattern.match(data_i):
                    data_i= datetime.datetime.strptime(data_i, "%d/%m/%Y")
                    if ctr.data_i != data_i:
                        ctr.data_i = data_i
                else:
                    errorlog += "Formato Incorreto na data de início /n"
                
                # Atualiza o valor da data_f se esta for valida. Caso o valor atual seja = Null, ou seja, o colaborador é ativo, desliga a flag is_active do usuário.
                if date_pattern.match(data_f):
                    data_f = datetime.datetime.strptime(data_f, "%d/%m/%Y")
                    if ctr.data_f != data_f:
                        if ctr.data_f is None:
                            ctr.colaborador.user.is_active = False
                            ctr.colaborador.user.save()
                        ctr.data_f = data_f
                elif data_f != "":
                    errorlog += "Formato Incorreto na data de Termino /n"

                if ctr.modelo_id != int(modelo):
                    ctr.modelo = ModeloContrato.objects.get(id=modelo)
                
                if ctr.direito_ferias != ferias:
                    ctr.direito_ferias = ferias

                if ctr.remuneracao != remuneracao:
                    ctr.remuneracao = remuneracao

                if ctr.tipo_remuneracao != tipo_remuneracao:
                    ctr.tipo_remuneracao = tipo_remuneracao
                    
                ctr.save()
            else:
                raise SuspiciousOperation("Você está acessando este link de uma forma incorreta")
        else:
            raise SuspiciousOperation("Você está acessando este link de uma forma incorreta")

        return HttpResponseRedirect('/HRP/perfil/' + str(colab_id) + "/?src=dados&errorlog=" + errorlog)
    else:
        raise PermissionDenied("Você não possui permissão para realizar esta operação!")


@login_required(login_url='/auth/login?next=/HRP/')
def download(request):
    if validate_user_perm(request.user):
        path = request.GET['path']
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type='application/force-download')
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
        raise Http404
    else:
        raise PermissionDenied("Você não possui permissão para realizar esta operação!")


# ------------------------- ALOCAÇÃO ----------------------------------
@login_required(login_url='/auth/login?next=/HRP/allocation/')
def allocation(request):
    if validate_user_perm(request.user, executor=True):
        ativos = Contrato.objects.filter(data_f__isnull=True).order_by('colaborador__nome').values_list('colaborador_id')
        colaboradores = Colaborador.objects.filter(id__in=ativos)
        allocations = Allocation.objects.order_by('resource').all()
        projetos = Projeto.objects.order_by('empresa', 'descricao').filter(ativa=True)

        breadcrumb = [["/", "Home"], ["/HRP/", "RH"], ["/HRP/allocation/", "Alocação"]]

        return render(request, 'HRP/resourcesAllocation.html', {"colaboradores": colaboradores, "allocations": allocations, "projetos": projetos, "breadcrumb": breadcrumb})
    else:
        raise PermissionDenied("Você não possui permissão para acessar esta página!")


@login_required(login_url='/auth/login?next=/HRP/allocation/')
def add_allocation(request):
    if request.method == 'POST':
        resource = Colaborador.objects.get(nome=request.POST['resource'])
        project = Projeto.objects.get(id=request.POST['project'])
        start_date = datetime.datetime.strptime(request.POST['start-date'], "%d/%m/%Y")
        end_date = datetime.datetime.strptime(request.POST['end-date'], "%d/%m/%Y")

        Allocation(resource=resource,
                   project=project,
                   start_date=start_date,
                   end_date=end_date).save()
        
        return HttpResponseRedirect('/HRP/allocation/')


@login_required(login_url='/auth/login?next=/HRP/allocation/')
def del_allocation(request):
    if request.method == 'POST':
        resource = Colaborador.objects.get(nome=request.POST['resource'])
        empresa = Empresa.objects.get(nome=request.POST['empresa'])
        project = Projeto.objects.get(empresa=empresa, descricao=request.POST['project'])
        start_date = datetime.datetime.strptime(request.POST['start_date'], "%d/%m/%Y")
        end_date = datetime.datetime.strptime(request.POST['end_date'], "%d/%m/%Y")

        del_objects = Allocation.objects.filter(resource=resource,
                                                project=project,
                                                start_date=start_date,
                                                end_date=end_date).all()
        
        if len(del_objects) == 1:
            del_objects[0].delete()

            return HttpResponse(dumps({"status": True}), content_type="application/json")

    return HttpResponse(dumps({"status": False}), content_type="application/json")
