import csv
import re
import os
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.conf import settings
from .models import Ranking, RegisterMoney
from .forms import PhotoUploadForm
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone

def importar_funcionarios(request):
    funcionarios = Ranking.objects.all()
    return render(request, 'funcionarios/import_csv.html', {'funcionarios': funcionarios})


def colab_import_csv(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Usuario nao autenticado'})

    if request.method == 'POST':
        print("post....")
        csv_file = request.FILES.get('csv_file')
        if csv_file and csv_file.name.endswith('.csv'):
            print("if....")
            try:
                print('try....')
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                delimiter = None
                for test_delimiter in [';', ',']:
                    try:
                        reader = csv.reader(decoded_file, delimiter=test_delimiter)
                        header = next(reader)
                        print(str(header) + str(reader))
                        delimiter = test_delimiter
                        break
                    except Exception:
                        continue

                if delimiter is None:
                    raise ValueError('Erro ao identificar o delimitador do arquivo CSV.')

                reader = csv.reader(decoded_file, delimiter=delimiter)
                next(reader)  # Pular o cabeçalho do CSV

                existing_cpfs = set(Ranking.objects.values_list('cpf', flat=True))
                results = {'created': 0, 'existing': 0}

                for row in reader:
                    print(str(row))
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

                response_data = {
                    'success': True,
                    'created': results['created'],
                    'existing': results['existing']
                }
            except ValueError as e:
                response_data = {'success': False, 'error': str(e)}
            return JsonResponse(response_data)
        else:
            return JsonResponse({'success': False, 'error': 'Por favor, faça upload de um arquivo CSV.'})

    return JsonResponse({'success': False, 'error': 'Método nao permitido'})

def colab_import_money(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Usuario nao autenticado'})

    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if csv_file and csv_file.name.endswith('.csv'):
            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                
                # Detectar delimitador
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
                    raise ValueError('Erro ao identificar o delimitador do arquivo CSV.')

                reader = csv.reader(decoded_file, delimiter=delimiter)
                next(reader)  # Pular o cabeçalho do CSV

                results = {'created': 0, 'errors': 0}
                for row in reader:
                    if len(row) >= 3:  # Verifica se a linha tem pelo menos 3 colunas
                        cpf_funcionario, cpf_cliente, valor_est = row[:3]

                        try:
                            # Validar e processar CPF do cliente
                            cpf_cliente = re.sub(r'\D', '', cpf_cliente)  # Remove caracteres nao numéricos do CPF

                            # Validar e processar CPF do funcionario
                            cpf_funcionario = re.sub(r'\D', '', cpf_funcionario)  # Remove caracteres nao numéricos do CPF
                            
                            # Verificar se o funcionario existe
                            try:
                                funcionario = Ranking.objects.get(cpf=cpf_funcionario)
                            except Ranking.DoesNotExist:
                                funcionario = None

                            # Criar o registro se o funcionario for valido
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

                response_data = {
                    'success': True,
                    'created': results['created'],
                    'errors': results['errors']
                }
            except ValueError as e:
                response_data = {'success': False, 'error': str(e)}
            return JsonResponse(response_data)
        else:
            return JsonResponse({'success': False, 'error': 'Por favor, faça upload de um arquivo CSV.'})

    return JsonResponse({'success': False, 'error': 'Método nao permitido'})

def colab_import_photo(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Usuario nao autenticado'})

    if request.method == 'POST':
        funcionario_id = request.POST.get('funcionario')
        photo = request.FILES.get('photo')
        
        if not funcionario_id or not photo:
            return JsonResponse({'success': False, 'error': 'Campos obrigatórios nao preenchidos.'})
        
        try:
            funcionario = Ranking.objects.get(id=funcionario_id)
            photo.name = f'{funcionario_id}_{funcionario.nome_completo.replace(" ", "_")}{os.path.splitext(photo.name)[1]}'
            funcionario.foto = photo
            funcionario.save()
            return JsonResponse({'success': True, 'message': 'Foto enviada com sucesso.'})
        except Ranking.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Funcionario nao encontrado.'})

    return JsonResponse({'success': False, 'error': 'Método nao permitido'})

def get_ranking_data():
    # Obter registros de RegisterMoney com status True
    registros = RegisterMoney.objects.filter(status=True)

    # Calcular o total vendido por cada funcionario
    total_vendido = registros.values('funcionario').annotate(total=Sum('valor_est')).order_by('-total')

    # Obter os IDs dos top 10 funcionarios
    top_funcionarios_ids = [item['funcionario'] for item in total_vendido[:5]]

    # Buscar os funcionarios com base nos IDs obtidos
    funcionarios = Ranking.objects.filter(id__in=top_funcionarios_ids)
    funcionarios_dict = {funcionario.id: funcionario for funcionario in funcionarios}

    # Preparar dados para o ranking
    valores = {}
    porcentagem = {}
    infoColab = []

    if total_vendido:
        max_valor = total_vendido[0]['total'] + 1000  # Evitar divisão por zero
    else:
        max_valor = 1

    for idx, item in enumerate(total_vendido[:10], start=1):
        funcionario_id = item['funcionario']
        valor_vendido = item['total']
        funcionario = funcionarios_dict.get(funcionario_id)

        if funcionario:
            valores[f'top_{idx}'] = valor_vendido
            porcentagem[f'top_{idx}'] = (valor_vendido / max_valor) * 100

            infoColab.append({
                'id': funcionario.id,
                'nome_completo': funcionario.nome_completo,
                'foto': funcionario.foto.url if funcionario.foto else '/static/img/ranking/default_image.png'
            })

    # Obter registros de RegisterMoney com status True para a lista
    registros_pagos = RegisterMoney.objects.filter(status=True).order_by('-data')  # Ordena por data (mais recente primeiro)
    lista_valores = [
        {
            'nome_completo': r.funcionario.nome_completo,
            'valor_est': r.valor_est,
            'data': r.data.strftime('%d-%m-%Y:%H-%M')  # Formata a data
        }
        for r in registros_pagos
    ]

    return {
        'valores': valores,
        'porcentagem': porcentagem,
        'infoColab': infoColab,
        'lista_valores': lista_valores  # Adiciona a lista de valores pagos
    }


def ranking(request):
    ranking_data = get_ranking_data()
    return JsonResponse(ranking_data)

def render_ranking(request):
    return render(request, 'funcionarios/ranking.html')

def lista_registros(request):
    registros = RegisterMoney.objects.filter(status=False)
    return render(request, 'funcionarios/table_val.html', {'registros': registros})

def alterar_status(request, id):
    try:
        registro = RegisterMoney.objects.get(id=id)
        registro.status = True
        registro.data = timezone.now()  # Atualiza para data e hora atual
        registro.save()
        return redirect('colab:lista_registros')  # Redireciona de volta para a lista
    except RegisterMoney.DoesNotExist:
        return HttpResponse("Registro não encontrado.", status=404)
