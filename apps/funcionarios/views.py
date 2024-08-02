import csv  # Utilizado para leitura de arquivos CSV
import re  # Utilizado para manipulação e validação de strings com expressões regulares
import os  # Utilizado para operações do sistema de arquivos, como manipulação de nomes de arquivos
from django.shortcuts import render, redirect, get_object_or_404  # Utilizado para renderizar templates e redirecionar URLs
from django.urls import reverse  # Utilizado para criação de URLs reversas
from django.contrib import messages  # Utilizado para adicionar mensagens de feedback ao usuário
from django.http import JsonResponse, HttpResponse  # Utilizado para retornar respostas JSON e HTTP
from django.core.files.storage import default_storage  # Utilizado para manipulação de arquivos de armazenamento
from django.conf import settings  # Utilizado para acessar configurações do projeto
from django.db.models import Sum, Max, F, Value
from django.db.models.functions import Coalesce
from django.utils import timezone  # Utilizado para manipulação de datas e horários
from django.utils.dateparse import parse_date
from .models import Ranking, RegisterMoney, RegisterMeta  # Importação dos modelos definidos
from .forms import PhotoUploadForm  # Importação do formulário de upload de fotos
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


# |-------------- RENDER IMPORT_CSV --------------|
def importar_funcionarios(request):
    if not request.user.is_authenticated:
        print('Usuário não autenticado')
        return redirect('usuarios:login')
    
    # Definir o primeiro e o último dia do mês vigente
    hoje = datetime.now()
    primeiro_dia_mes = hoje.replace(day=1)
    ultimo_dia_mes = (primeiro_dia_mes + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    
    range_inicio = primeiro_dia_mes.date()
    range_fim = ultimo_dia_mes.date()
    
    # Obter todos os registros necessários com o filtro de data
    funcionarios = Ranking.objects.all()
    print('Funcionários:', funcionarios)
    registros = RegisterMoney.objects.filter(data__range=[range_inicio, range_fim])
    metas = RegisterMeta.objects.all()  # Obter os dados da tabela de metas

    # Preparar a lista de funcionários com os dados necessários
    funcionarios_list = [
        {
            'id': funcionario.id,
            'nome_completo': funcionario.nome_completo,
            'cpf': funcionario.cpf
        }
        for funcionario in funcionarios
    ]
    print(str(funcionarios_list))

    context = {
        'funcionarios': funcionarios_list,
        'registros': registros,
        'metas': metas  # Enviar os dados da tabela de metas
    }

    # Renderizar o template com os dados adicionais
    return render(request, 'funcionarios/import_csv.html', context)

# |-------------- ACTION IMPORT_CSV:FUNCIONARIOS --------------|
def colab_import_csv(request):
    if not request.user.is_authenticated:
        print('Usuario nao autenticado')
        return redirect('usuarios:login')

    if request.method == 'POST':
        print("CSV post....")
        csv_file = request.FILES.get('csv_file')
        if csv_file and csv_file.name.endswith('.csv'):
            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                delimiter = None
                for test_delimiter in [';', ',']:
                    try:
                        reader = csv.reader(decoded_file, delimiter=test_delimiter)
                        header = next(reader)
                        delimiter = test_delimiter
                        break
                    except Exception:
                        continue

                if delimiter is None:
                    print('Erro ao identificar o delimitador do arquivo CSV.')
                    return redirect('colab:importar_funcionarios')

                reader = csv.reader(decoded_file, delimiter=delimiter)
                next(reader)  # Pular o cabeçalho do CSV

                existing_cpfs = set(Ranking.objects.values_list('cpf', flat=True))
                results = {'created': 0, 'existing': 0}

                for row in reader:
                    if len(row) == 5:
                        foto, nome_completo, cpf, setor, localidade = row
                        cpf = re.sub(r'\D', '', cpf)
                        if cpf not in existing_cpfs:
                            Ranking.objects.create(
                                nome_completo=nome_completo,
                                cpf=cpf,
                                setor=setor,
                                localidade=localidade
                            )
                            results['created'] += 1
                        else:
                            results['existing'] += 1

                print('Resultados: ', results)
                return redirect('colab:importar_funcionarios')

            except ValueError as e:
                print('Erro: ', e)
                return redirect('colab:importar_funcionarios')
        else:
            print('Por favor, faça upload de um arquivo CSV.')
            return redirect('colab:importar_funcionarios')

    print('Método nao permitido')
    return redirect('colab:importar_funcionarios')

# |-------------- ACTION IMPORT_MANUAL:FUNCIONARIOS --------------|
def colab_import_manual(request):
    if not request.user.is_authenticated:
        print('Usuario nao autenticado')
        return redirect('usuarios:login')

    if request.method == 'POST':
        print("Form manual post....")
        nome_completo = request.POST.get('nome_completo')
        cpf = request.POST.get('cpf')
        setor = request.POST.get('setor')
        localidade = request.POST.get('localidade')

        cpf = re.sub(r'\D', '', cpf)
        if not Ranking.objects.filter(cpf=cpf).exists():
            Ranking.objects.create(
                nome_completo=nome_completo,
                cpf=cpf,
                setor=setor,
                localidade=localidade
            )
            print('Funcionario criado manualmente')
        else:
            print('CPF já existe')
        return redirect('colab:importar_funcionarios')

    print('Método nao permitido')
    return redirect('colab:importar_funcionarios')

# |-------------- ACTION IMPORT_PHOTO --------------|
def colab_import_photo(request):
    if not request.user.is_authenticated:
        print('Usuario nao autenticado')
        return redirect('usuarios:login')

    if request.method == 'POST':
        funcionario_id = request.POST.get('funcionario')
        photo = request.FILES.get('photo')

        if not funcionario_id or not photo:
            print('Campos obrigatórios nao preenchidos.')
            return redirect('colab:importar_funcionarios')

        try:
            funcionario = Ranking.objects.get(id=funcionario_id)
            photo.name = f'{funcionario_id}_{funcionario.nome_completo.replace(" ", "_")}{os.path.splitext(photo.name)[1]}'
            funcionario.foto = photo
            funcionario.save()
            print('Foto enviada com sucesso.')
            return redirect('colab:importar_funcionarios')
        except Ranking.DoesNotExist:
            print('Funcionario nao encontrado.')
            return redirect('colab:importar_funcionarios')

    print('Método nao permitido')
    return redirect('colab:importar_funcionarios')

# |-------------- ACTION IMPORT_CSV:MONEY --------------|
def money_import_csv(request):
    if not request.user.is_authenticated:
        print('Usuario nao autenticado')
        return redirect('usuarios:login')

    if request.method == 'POST':
        print("CSV post....")
        csv_file = request.FILES.get('csv_file')
        if csv_file and csv_file.name.endswith('.csv'):
            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                delimiter = None
                for test_delimiter in [';', ',']:
                    try:
                        reader = csv.reader(decoded_file, delimiter=test_delimiter)
                        header = next(reader)
                        delimiter = test_delimiter
                        break
                    except Exception:
                        continue

                if delimiter is None:
                    print('Erro ao identificar o delimitador do arquivo CSV.')
                    return redirect('colab:importar_funcionarios')

                reader = csv.reader(decoded_file, delimiter=delimiter)
                next(reader)  # Pular o cabeçalho do CSV

                results = {'created': 0, 'errors': 0}
                for row in reader:
                    if len(row) >= 3:  # Verifica se a linha tem pelo menos 3 colunas
                        cpf_funcionario, cpf_cliente, valor_est = row[:3]

                        try:
                            cpf_cliente = re.sub(r'\D', '', cpf_cliente)
                            cpf_funcionario = re.sub(r'\D', '', cpf_funcionario)
                            
                            try:
                                funcionario = Ranking.objects.get(cpf=cpf_funcionario)
                            except Ranking.DoesNotExist:
                                funcionario = None

                            if funcionario:
                                RegisterMoney.objects.create(
                                    funcionario=funcionario,
                                    cpf_cliente=cpf_cliente,
                                    valor_est=float(valor_est),
                                    status=False  # Valor padrao
                                )
                                results['created'] += 1
                            else:
                                results['errors'] += 1

                        except Exception as e:
                            results['errors'] += 1
                            print(f"Erro ao processar linha: {e}")

                print('Resultados: ', results)
                return redirect('colab:importar_funcionarios')

            except ValueError as e:
                print('Erro: ', e)
                return redirect('colab:importar_funcionarios')
        else:
            print('Por favor, faça upload de um arquivo CSV.')
            return redirect('colab:importar_funcionarios')

    print('Método nao permitido')
    return redirect('colab:importar_funcionarios')

# |-------------- ACTION IMPORT_MANUAL:MONEY --------------|
def money_import_manual(request):
    if not request.user.is_authenticated:
        print('Usuário não autenticado')
        return redirect('usuarios:login')

    if request.method == 'POST':
        print("Form manual post....")
        funcionario_id = request.POST.get('funcionario')
        print(str(funcionario_id))
        valor_est = request.POST.get('valor_est')
        print(str(valor_est))

        try:
            funcionario = Ranking.objects.get(id=funcionario_id)
            print(str(funcionario))
            cpf_funcionario = funcionario.cpf  # Obtém o CPF do funcionário

            # Remover caracteres não numéricos do CPF
            if cpf_funcionario:
                cpf_funcionario = re.sub(r'\D', '', cpf_funcionario)
            else:
                print('CPF do funcionário não encontrado')
                return redirect('colab:importar_funcionarios')

            RegisterMoney.objects.create(
                funcionario=funcionario,
                cpf_cliente=None,  # CPF do cliente é opcional
                valor_est=float(valor_est),
                status=False  # Valor padrão
            )
            print('Valor cadastrado manualmente')
        except Ranking.DoesNotExist:
            print('Funcionário não encontrado')

        return redirect('colab:importar_funcionarios')

    print('Método não permitido')
    return redirect('colab:importar_funcionarios')

# |-------------- ACTION IMPORT_METAS --------------|
def import_metas(request):
    if not request.user.is_authenticated:
        print('Usuário não autenticado')
        return redirect('usuarios:login')

    if request.method == 'POST':
        valor = request.POST.get('valor')
        setor = request.POST.get('setor')
        range_data_inicio = request.POST.get('range_data_inicio')
        range_data_final = request.POST.get('range_data_final')
        descricao = request.POST.get('descricao')  # Adicionado para o campo descricao

        try:
            valor = float(valor.replace('R$', '').replace('.', '').replace(',', '.'))
            data_inicio = parse_date(range_data_inicio)
            data_final = parse_date(range_data_final)

            if data_inicio and data_final:
                if data_inicio > data_final:
                    raise ValueError('A data final deve ser posterior à data inicial.')

                RegisterMeta.objects.create(
                    valor=valor,
                    setor=setor,
                    range_data_inicio=data_inicio,  # Usando o nome correto
                    range_data_final=data_final,    # Usando o nome correto
                    descricao=descricao             # Adicionado para o campo descricao
                )
                print('Meta criada com sucesso.')
                return redirect('colab:importar_funcionarios')  # Corrigido o redirecionamento
            else:
                raise ValueError('Datas inválidas.')

        except ValueError as e:
            print(f'Erro: {e}')
            return redirect('colab:importar_funcionarios')  # Corrigido o redirecionamento

    print('Método não permitido')
    return redirect('colab:importar_funcionarios')  # Corrigido o redirecionamento

def get_ranking_data(setor):
    # Receber sem filtro
    infoColab = Ranking.objects.all()
    valores = RegisterMoney.objects.all()
    metas = RegisterMeta.objects.all()

    # Print para log/debug
    print("infoColab: " + str(infoColab))
    print("valores: " + str(valores))
    print("metas: " + str(metas))

    # Variáveis para o mês atual
    mes_atual = timezone.now().month
    range_inicio = timezone.make_aware(datetime(timezone.now().year, mes_atual, 1))
    range_fim = timezone.make_aware(datetime(timezone.now().year, mes_atual, 1) + relativedelta(months=1) - timedelta(seconds=1))

    # Metas ativas e valores ativos com filtro por status True
    metas_ativas = metas.filter(status=True)
    valores_ativos = valores.filter(status=True)

    # Print para log/debug
    print("metas_ativas: " + str(metas_ativas))
    print("valores_ativos: " + str(valores_ativos))

    # Encontrar a meta geral
    meta_geral = None
    prioridade = ['Bônus', 'Geral', 'Equipe']

    for descricao in prioridade:
        meta = metas_ativas.filter(descricao=descricao).order_by('-valor').first()
        if meta:
            meta_geral = meta
            break

    if not meta_geral:
        return {
            'ranking': [],
            'porcentagens': [],
            'infoColab_lista': [],
            'meta': {
                'titulo': 'REGISTRAR META GERAL',
                'descricao': 'Não encontrado',
                'setor': 'Nenhum',
                'valor_pago': 0,
                'valor_faltante': 0,
                'porcentagem': 0
            }
        }

    # Calcular a Meta Individual e Top 5
    if meta_geral.valor != 0:
        top_5 = valores_ativos.filter(
            funcionario__setor=meta_geral.setor,
            data__range=[range_inicio, range_fim]
        ).values('funcionario').annotate(total=Sum('valor_est')).order_by('-total')[:5]

        print("top_5: " + str(top_5))

        top_funcionarios_ids = [item['funcionario'] for item in top_5]
        funcionarios = infoColab.filter(id__in=top_funcionarios_ids)
        print("funcionarios: " + str(funcionarios))

        meta_individual = metas_ativas.filter(descricao='Individual').order_by('-valor').first()
        print("meta_individual: " + str(meta_individual))

        valor_pago = valores_ativos.filter(data__range=[range_inicio, range_fim]).aggregate(total_pago=Sum('valor_est'))['total_pago'] or 0
        valor_total_meta = meta_geral.valor
        valor_faltante = float(valor_total_meta) - float(valor_pago)
        porcentagem_meta_geral = (float(valor_pago) / float(valor_total_meta)) * 100 if valor_total_meta > 0 else 0

        print("meta_geral.valor_faltante: " + str(valor_faltante))
        print("meta_geral.porcentagem: " + str(porcentagem_meta_geral))
    else:
        valor_pago = 0
        valor_faltante = 0
        porcentagem_meta_geral = 0

    # Preparar dados para o ranking
    infoColab_lista = []
    ranking = []
    porcentagens = []

    for item in top_5:
        funcionario_id = item['funcionario']
        valor_sum_colab = valores_ativos.filter(
            funcionario_id=funcionario_id,
            data__range=[range_inicio, range_fim]
        ).aggregate(total=Sum('valor_est'))['total'] or 0
        funcionario = funcionarios.get(id=funcionario_id)

        if funcionario:
            ranking.append({
                'funcionario_id': funcionario.id,
                'valor': valor_sum_colab
            })

            porcentagem = (valor_sum_colab / float(meta_individual.valor)) * 100 if meta_individual else 0
            if porcentagem > 100:
                porcentagem = 100

            porcentagens.append({
                'funcionario_id': funcionario.id,
                'porcentagem': porcentagem
            })

            infoColab_lista.append({
                'id': funcionario.id,
                'nome_completo': funcionario.nome_completo,
                'foto': funcionario.foto.url if funcionario.foto else '/static/img/ranking/default_image.png'
            })

    # Print para log/debug
    print("ranking: " + str(ranking))
    print("porcentagens: " + str(porcentagens))
    print("infoColab_lista: " + str(infoColab_lista))

    context = {
        'ranking': ranking,
        'porcentagens': porcentagens,
        'infoColab_lista': infoColab_lista,
        'meta': {
            'titulo': meta_geral.titulo,
            'descricao': meta_geral.descricao,
            'setor': meta_geral.setor,
            'valor_pago': valor_pago,
            'valor_faltante': valor_faltante,
            'porcentagem': porcentagem_meta_geral
        }
    }
    print("context: " + str(context))

    return context

# |-------------- INTERMEDIARIO RANKING --------------|
def ranking(request):
    setor = 'Geral'  # Defina um setor padrão se necessário
    ranking_data = get_ranking_data(setor)
    return JsonResponse(ranking_data)

# |-------------- RENDER RANKING --------------|
def render_ranking(request):
    return render(request, 'funcionarios/ranking.html')

# |-------------- SOLICITAÇÃO:RENDER TABLE_VAL --------------|
def lista_registros(request):
    if not request.user.is_authenticated:
        print('Usuario nao autenticado')
        return redirect('usuarios:login')
    registros = RegisterMoney.objects.filter(status=False)
    return render(request, 'funcionarios/table_val.html', {'registros': registros})

# |-------------- ACTION TABLE_VAL --------------|
def alterar_status(request, id):
    if not request.user.is_authenticated:
        print('Usuario nao autenticado')
        return redirect('usuarios:login')
    try:
        registro = RegisterMoney.objects.get(id=id)
        registro.status = True
        registro.data = timezone.now()  # Atualiza para data e hora atual
        registro.save()
        return redirect('colab:lista_registros')  # Redireciona de volta para a lista
    except RegisterMoney.DoesNotExist:
        return HttpResponse("Registro não encontrado.", status=404)

def alterar_status_meta(request, id):
    if not request.user.is_authenticated:
        print('Usuario nao autenticado')
        return redirect('usuarios:login')
    if request.method == 'GET':
        meta = get_object_or_404(RegisterMeta, id=id)
        meta.status = not meta.status  # Alterna o status entre True e False
        meta.save()
        return redirect('colab:import_metas')