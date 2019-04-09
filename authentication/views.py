from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.exceptions import SuspiciousOperation
from HRP.models import Colaborador
from random import sample
from django.conf import settings

def userLogin(request):

    breadcrumb = [["/auth","Login"]]
    
    if request.method == 'POST':
        username = request.POST['inputName']
        password = request.POST['inputPassword']
        user = authenticate(username=username, password=password)

        if user is not None:
            if  user.is_active:
                login(request, user)
                if 'next' in request.GET:
                    return HttpResponseRedirect(request.GET['next'])
                else:
                    return HttpResponseRedirect('/HRP/')
            else:
                return render(request, 'Authentication/login.html', {"errorlog":["Usuário Inativo"], "breadcrumb":breadcrumb})    
        else:
            # Return an 'invalid login' error message
            return render(request, 'Authentication/login.html', {"errorlog":["Login ou senha incorretos"], "breadcrumb":breadcrumb})
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        else:
            return render(request, 'Authentication/login.html', {"errorlog":None, "breadcrumb":breadcrumb})

def userLogout(request):
    logout(request)
    return HttpResponseRedirect('/auth/')

def userRegister(username,password,is_manager=False,is_executor=True,is_RH=False,is_financeiro=False):
	
    user = User.objects.create_user(username=username, password=password, is_manager=is_manager, is_executor=is_executor, is_financeiro=is_financeiro, is_RH=is_RH)
    return user

def alter_user_email(user, mail_content):
    mail_subject = 'Credenciais da intrabix alteradas com sucesso'
    destinatarios = [user.colaborador.email]
    send_mail(mail_subject, mail_content, settings.EMAIL_SENDER, destinatarios, fail_silently=False)


def validate_user_perm(user, manager=False, executor=False, active=True, financeiro = False, RH = False ):
    valid = True
    if active:
        valid = valid and user.is_active
    if manager:
        valid = valid and user.is_manager
    else:
        if user.is_manager:
            valid = valid and user.is_manager
        elif executor:
            valid = valid and user.is_executor
        elif financeiro:
            valid = valid and user.is_financeiro
        elif RH:
            valid = valid and user.is_RH

    return valid

def rec_pass(request):
    if request.method == 'POST':
        breadcrumb = [["/auth","Login"]]
        
        username = request.POST['inputName']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                user = Colaborador.objects.get(email=username).user
            except:
                return render(request, 'Authentication/login.html', {"errorlog":["Não existe um usuário com esse login ou e-mail"], "breadcrumb":breadcrumb})
        
        password = random_password_generator()
        user.set_password(password)
        user.save()


        mail_content = 'As credenciais do seu usuário na intrabix foram alteradas com sucesso!\n\nCredenciais alteradas:\n'
        mail_content += " - Login: " + user.username + "\n"
        mail_content += " - Senha: " + password + "\n"
        mail_content += " - E-mail: " + user.colaborador.email + "\n"

        alter_user_email(user,mail_content)

        return render(request, 'Authentication/login.html', {"errorlog":["Um e-mail com as novas credenciais foi enviado para " + user.colaborador.email], "breadcrumb":breadcrumb})
    else:
        return userLogin(request)

@login_required(login_url='/auth/login?next=/')
def account(request):
    if validate_user_perm(request.user):
        log = list()
        breadcrumb = [["/", "Home"],["/auth","Gerenciar Conta"]]
        
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            email = request.POST['email']

            flag = False
            mail_content = 'As credenciais do seu usuário na intrabix foram alteradas com sucesso!\n\nCredenciais alteradas:\n'
            if username != request.user.username:
                
                try:
                    User.objects.get(username=username)
                except User.DoesNotExist: 
                    flag = True
                    request.user.username = username
                    log.append("Nome de usuário alterado com sucesso")
                    mail_content += " - Login: " + username + "\n"
                else:
                    log.append("Este nome de usuário já existe")
            
            if password != "" and not check_password(password, request.user.password):
                flag = True
                request.user.set_password(password)
                log.append("Senha alterada com sucesso")
                mail_content += " - Senha: " + password + "\n"
            
            if email != request.user.colaborador.email:
                try:
                    Colaborador.objects.get(email=email)
                except Colaborador.DoesNotExist:
                    request.user.colaborador.email = email
                    request.user.colaborador.save()
                    log.append("E-mail alterado com sucesso")
                    mail_content += "E-mail: " + email + "\n"
                else:
                    log.append("Seu e-mail não foi alterado por que já existe um usuário cadastrado com este e-mail.")

            if flag:
                alter_user_email(request.user, mail_content)
                request.user.save()
                logout(request)
                return render(request, 'Authentication/login.html', {"errorlog":log, "breadcrumb":breadcrumb})    
    
    
    return render(request, 'Authentication/account.html', {'log':log, 'breadcrumb':breadcrumb})

def random_password_generator():
    possible_chars = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%&()?"
    passlen = 8

    password =  "".join(sample(possible_chars,passlen))
    return password