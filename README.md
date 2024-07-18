# 📊 Django Data Management System

Este é um sistema de gerenciamento de dados desenvolvido em Django, que permite a importação, consulta e gerenciamento de dados de clientes e débitos. O sistema inclui funcionalidades para importar dados de arquivos CSV, realizar consultas detalhadas sobre clientes e gerenciar informações relacionadas a débitos.

## 🚀 Instalação

1. **Clone o repositório:**
   <<bash
   git clone https://github.com/username/repository.git
   cd repository
   >>

2. **Crie um ambiente virtual e ative-o:**
   <<bash
   python -m venv env
   source env/bin/activate  # Para Windows use `env\Scripts\activate`
   >>

3. **Instale as dependências:**
   <<bash
   pip install -r requirements.txt
   >>

4. **Configure o banco de dados:**
   <<bash
   python manage.py migrate
   >>

5. **Crie um superusuário para acessar o admin:**
   <<bash
   python manage.py createsuperuser
   >>

6. **Inicie o servidor:**
   <<bash
   python manage.py runserver
   >>

## 📄 Uso

- **Consulta de Cliente:**
  - Acesse `http://127.0.0.1:8000/consulta_cliente` para buscar clientes pelo CPF.
  - Visualize as informações do cliente acessando a URL com o CPF: `http://127.0.0.1:8000/ficha_cliente/<cpf>`.

- **Gerenciamento de Dados:**
  - Acesse `http://127.0.0.1:8000/gerenciamento` para importar dados de um arquivo CSV.
  - Certifique-se de que o CSV contenha as colunas esperadas para uma importação bem-sucedida.

## 🔧 Contribuição

1. Faça um fork do repositório.
2. Crie uma nova branch (`git checkout -b feature-branch`).
3. Faça suas mudanças e adicione commits (`git commit -am 'Adiciona nova feature'`).
4. Envie suas mudanças para o repositório remoto (`git push origin feature-branch`).
5. Abra um pull request.

## 📝 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ⚙️ Funcionalidades

### Consulta de Cliente

<<python
from django.shortcuts import render, redirect
from django.http import JsonResponse
from apps.consultas.models import Cliente
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def consulta_cliente(request):
    cpf_cliente = request.GET.get('cpf_cliente', None)
    if cpf_cliente:
        try:
            cliente = Cliente.objects.get(cpf=cpf_cliente)
            return redirect('consulta:ficha_cliente_cpf', cpf=cpf_cliente)
        except Cliente.DoesNotExist:
            return JsonResponse({'error': 'Cliente não encontrado'}, status=404)
    else:
        return render(request, 'consultas/consulta_cliente.html')
>>

### Importação de Dados CSV

<<python
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import csv

@login_required
@require_http_methods(["GET", "POST"])
def gerenciamento(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        expected_fields = [
            # Lista de campos esperados
        ]
        # Processamento do arquivo CSV
        # ...
>>

### Funções de Usuário

<<python
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib import messages
from apps.usuarios.forms import LoginForms, RegistroForms
from django.contrib.auth.models import User
from apps.consultas.models import Cliente, MatriculaDebitos

def login_index(request):
    form = LoginForms()
    if request.method == 'POST':
        form = LoginForms(request.POST)
        if form.is_valid():
            nome = form['nome_login'].value()
            senha = form['senha'].value()
            usuario = authenticate(request, username=nome, password=senha)
            if usuario is not None:
                login(request, usuario)
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

            nome = form['nome_cadastro'].value()
            email = form['email'].value()
            senha = form['senha_1'].value()

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
    auth_logout(request)
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
>>

---

Para mais informações, consulte a [documentação do Django](https://docs.djangoproject.com/en/stable/).
