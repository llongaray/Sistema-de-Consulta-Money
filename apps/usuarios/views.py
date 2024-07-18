from django.shortcuts import render, redirect

from apps.usuarios.forms import LoginForms, RegistroForms

from django.contrib.auth.models import User

from django.contrib import auth
from apps.consultas.models import Cliente, MatriculaDebitos
from django.contrib import messages

def login_index(request):
    form = LoginForms()

    if request.method == 'POST':
        form = LoginForms(request.POST)

        if form.is_valid():
            nome = form['nome_login'].value()
            senha = form['senha'].value()

        usuario = auth.authenticate(
            request,
            username=nome,
            password=senha
        )
        if usuario is not None:
            auth.login(request, usuario)
            messages.success(request, f'{nome} logado com sucesso!')
            return redirect('usuarios:welcome')
        else:
            messages.error(request, 'Erro ao efetuar login')
            return redirect('usuarios:login')

    return render(request, 'usuarios/login.html', {'form': form})

def register_index(request):
    form = RegistroForms()

    if request.method == 'POST':
        form = RegistroForms(request.POST)

        if form.is_valid():
            if form["senha_1"].value() != form["senha_2"].value():
                messages.error(request, 'Senhas não são iguais')
                return redirect('usuarios:register')

            nome=form['nome_cadastro'].value()
            email=form['email'].value()
            senha=form['senha_1'].value()

            if User.objects.filter(username=nome).exists():
                messages.error(request, 'Usuário já existente')
                return redirect('usuarios:register')

            usuario = User.objects.create_user(
                username=nome,
                email=email,
                password=senha
            )
            usuario.save()
            messages.success(request, 'Cadastro efetuado com sucesso!')
            return redirect('usuarios:login')

    return render(request, 'usuarios/register.html', {'form': form})

def logout(request):
    auth.logout(request)  # Passando o objeto request para a função logout()
    messages.success(request, 'Logout efetuado com sucesso!')
    return redirect('usuarios:login')

def welcome(request):
    # Contar o número total de clientes
    total_clientes = Cliente.objects.count()

    # Contar o número total de débitos (considerando cada débito como uma linha na tabela)
    total_debitos = MatriculaDebitos.objects.count()

    context = {
        'total_clientes': total_clientes,
        'total_debitos': total_debitos,
    }
    return render(request, 'usuarios/welcome.html', context)