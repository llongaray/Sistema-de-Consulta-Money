from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Cliente, MatriculaDebitos
import csv
from django.db.models import Q
import logging
from django.db import transaction
import time
from django.utils.timezone import now
from datetime import timedelta
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required


# Configurando o logger
logger = logging.getLogger(__name__)

def ficha_cliente(request, cpf):
    cliente = get_object_or_404(Cliente, cpf=cpf)
    matriculas_db = MatriculaDebitos.objects.filter(cliente=cliente)
    
    margens = {}  # Dicionário para armazenar as margens
    cont_margem = 0  # Variável para contar as margens
    
    matriculas = []  # Lista para armazenar as matrículas
    
    for matricula in matriculas_db:
        print("for matriculas")
        matriculas.append({
            'matricula': matricula.matricula,
            'rubrica': matricula.rubrica,
            'banco': matricula.banco,
            'orgao': matricula.orgao,
            'pmt': matricula.pmt,
            'prazo': matricula.prazo,
            'tipo_contrato': matricula.tipo_contrato,
            'contrato': matricula.contrato,
            'creditos': matricula.creditos,
            'liquido': matricula.liquido,
            'exc_soma': matricula.exc_soma,
            'margem': matricula.margem,
            'base_calc': matricula.base_calc,
            'bruta_5': matricula.bruta_5,
            'utilz_5': matricula.utilz_5,
            'beneficio_bruta_5': matricula.beneficio_bruta_5,
            'beneficio_utilizado_5': matricula.beneficio_utilizado_5,
            'bruta_35': matricula.bruta_35,
            'utilz_35': matricula.utilz_35,
            'bruta_70': matricula.bruta_70,
            'utilz_70': matricula.utilz_70,
            'saldo_35': matricula.saldo_35,
            'saldo_5': matricula.saldo_5,
            'beneficio_saldo_5': matricula.beneficio_saldo_5,
            'arq_upag': matricula.arq_upag,
            'exc_qtd': matricula.exc_qtd,
        })
        
        # Verifica se é a primeira margem
        if cont_margem == 0:
            margens[(matricula.saldo_35, matricula.saldo_5, matricula.beneficio_saldo_5)] = {
                'saldo_35': matricula.saldo_35,
                'saldo_5': matricula.saldo_5,
                'beneficio_saldo_5': matricula.beneficio_saldo_5,
            }
            cont_margem += 1
        else:
            # Verifica se a margem atual já está no dicionário
            if (matricula.saldo_35, matricula.saldo_5, matricula.beneficio_saldo_5) not in margens:
                margens[(matricula.saldo_35, matricula.saldo_5, matricula.beneficio_saldo_5)] = {
                    'saldo_35': matricula.saldo_35,
                    'saldo_5': matricula.saldo_5,
                    'beneficio_saldo_5': matricula.beneficio_saldo_5,
                }

    # Verifica se há duplicatas na lista de margens (considerando apenas os números antes da vírgula e os dois primeiros números depois da vírgula)
    margens_unicas = {}
    for chave, valor in margens.items():
        rounded_saldo_35 = round(valor['saldo_35'], 2)
        rounded_saldo_5 = round(valor['saldo_5'], 2)
        rounded_beneficio_saldo_5 = round(valor['beneficio_saldo_5'], 2)
        
        chave_arredondada = (rounded_saldo_35, rounded_saldo_5, rounded_beneficio_saldo_5)
        
        if chave_arredondada not in margens_unicas:
            margens_unicas[chave_arredondada] = valor

    context = {
        'cliente': {
            'nome': cliente.nome,
            'cpf': cliente.cpf,
            'uf': cliente.uf,
            'upag': cliente.upag,
            'matricula_instituidor': cliente.matricula_instituidor,
            'situacao_funcional': cliente.situacao_funcional,
            'rjur': cliente.rjur,
        },
        'margens': list(margens_unicas.values()),  # Passa a lista de margens únicas ao contexto
        'matriculas': matriculas,  # Adiciona a lista de matrículas ao contexto
    }
    print("fim ficha")
    return render(request, 'consultas/ficha_cliente.html', context)


@require_http_methods(["POST", "GET"])
def consulta_cliente(request):
    mensagem = ""

    if request.method == "POST":
        cpf_cliente = request.POST.get('cpf_cliente', None)
        if cpf_cliente:
            cpf_cliente_limpo = cpf_cliente.replace('.', '').replace('-', '')
            try:
                cliente = Cliente.objects.get(cpf=cpf_cliente_limpo)
                return redirect('consulta:ficha_cliente_cpf', cpf=cpf_cliente_limpo)
            except Cliente.DoesNotExist:
                mensagem = "Cliente não encontrado!"

    return render(request, 'consultas/consulta_cliente.html', {'mensagem': mensagem})



def normalize_cpf(cpf):
    # Remove todos os caracteres não numéricos
    cpf_numerico = ''.join(filter(str.isdigit, cpf))

    # Completa com zeros à esquerda até ter 11 dígitos
    cpf_com_zeros = cpf_numerico.zfill(11)

    return cpf_com_zeros

def parse_float(value, default="0.00"):
    try:
        return "{:.2f}".format(float(value.replace('.', '').replace(',', '.'))) if value.strip() else default
    except ValueError:
        return default


@require_http_methods(["GET", "POST"])
def gerenciamento(request):
    if not request.user.is_authenticated:
        return redirect('usuarios:login')

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        # Headers esperados em diferentes formatos
        expected_headers_sets = [
            [
                "BANCO", "ORGAO", "MATRICULA", "UPAG", "UF", "NOME", "CPF", "RUBRICA", "PMT", "PRAZO",
                "TIPO CONTRATO", "CONTRATO", "Matricula", "Base Calc", "Bruta 5%", "Utilz 5%",
                "Saldo 5%", "Beneficio Bruta 5%", "Beneficio Utilizado 5%", "Beneficio Saldo 5%", "Bruta 35%",
                "Utilz 35%", "Saldo 35%", "Bruta 70%", "Utilz 70%", "Saldo 70%", "Créditos", "Débitos",
                "Líquido", "ARQ. UPAG", "EXC QTD", "EXC Soma", "RJUR", "Sit Func", "Margem"
            ],
            [
                "BANCO", "ORGAO", "MATRICULA", "UPAG", "UF", "NOME", "CPF", "RUBRICA", "PMT", "PRAZO",
                "TIPO CONTRATO", "CONTRATO", "Orgão", "Matricula", "Base Calc", "Bruta 5%", "Utilz 5%",
                "Saldo 5%", "Beneficio Bruta 5%", "Beneficio Utilizado 5%", "Beneficio Saldo 5%", "Bruta 35%",
                "Utilz 35%", "Saldo 35%", "Bruta 70%", "Utilz 70%", "Saldo 70%", "Créditos", "Débitos",
                "Líquido", "ARQ. UPAG", "EXC QTD", "EXC Soma", "RJUR", "Sit Func", "Margem"
            ],
            [
                "BANCO", "ORGAO", "MATRICULA INSTITUIDOR", "MATRICULA", "UPAG", "UF", "NOME", "CPF", "RUBRICA",
                "PMT", "PRAZO", "TIPO CONTRATO", "CONTRATO", "Orgão", "Instituidor", "Matricula", "Base Calc",
                "Bruta 5%", "Utilz 5%", "Saldo 5%", "Beneficio Bruta 5%", "Beneficio Utilizado 5%",
                "Beneficio Saldo 5%", "Bruta 35%", "Utilz 35%", "Saldo 35%", "Bruta 70%", "Utilz 70%", "Saldo 70%",
                "Créditos", "Débitos", "Líquido", "ARQ. UPAG", "EXC QTD", "EXC Soma", "RJUR", "Sit Func", "Margem"
            ]
        ]

        try:
            # Lê o arquivo CSV
            csv_file.seek(0)
            csv_reader = csv.DictReader(csv_file.read().decode('utf-8-sig').splitlines(), delimiter=';', quotechar='"')
            csv_header = csv_reader.fieldnames

            # Verifica se o header do CSV corresponde a algum dos formatos esperados
            if not any(set(expected_headers_set) <= set(csv_header) for expected_headers_set in expected_headers_sets):
                return JsonResponse({'status': 'error', 'message': 'Header do CSV não corresponde ao formato esperado.'}, status=400)

            # Encontrar o header esperado
            expected_fields = next(set(expected_headers_set) for expected_headers_set in expected_headers_sets if set(expected_headers_set) <= set(csv_header))
            missing_fields = [field for field in expected_fields if field not in csv_header]
            if missing_fields:
                return JsonResponse({'status': 'error', 'message': f'Colunas ausentes no CSV: {", ".join(missing_fields)}'}, status=400)

            total_rows = sum(1 for _ in csv_reader)
            csv_file.seek(0)
            csv_reader = csv.DictReader(csv_file.read().decode('utf-8-sig').splitlines(), delimiter=';', quotechar='"')

            processed_rows = 0
            for row in csv_reader:
                processed_rows += 1
                cliente_add = False
                debito_add = False

                if any(value == "#N/D" for value in row.values()):
                    continue

                cpf_normalizado = normalize_cpf(row.get('CPF', ''))
                try:
                    cliente = Cliente.objects.get(cpf=cpf_normalizado)
                except Cliente.DoesNotExist:
                    cliente = Cliente.objects.create(
                        cpf=cpf_normalizado,
                        nome=row.get('NOME', ''),
                        uf=row.get('UF', ''),
                        upag=row.get('UPAG', ''),
                        matricula_instituidor=row.get('MATRICULA INSTITUIDOR', ''),
                        situacao_funcional=row.get('Sit Func', ''),
                        rjur=row.get('RJUR', '')
                    )
                    cliente_add = True

                pmt = parse_float(row.get('PMT', '0'))
                prazo = row.get('PRAZO', '').strip()
                exc_qtd = int(row.get('EXC QTD', '0').strip() or 0)

                all_debitos = MatriculaDebitos.objects.filter(cliente=cliente)
                debitos_same_pmt = all_debitos.filter(pmt=pmt)
                debitos_same_pmt_prazo = debitos_same_pmt.filter(prazo=prazo)
                existing_debitos_dict = {debito.id: debito for debito in debitos_same_pmt_prazo}

                if not existing_debitos_dict:
                    MatriculaDebitos.objects.create(
                        cliente=cliente,
                        matricula=row.get('MATRICULA', ''),
                        rubrica=row.get('RUBRICA', ''),
                        banco=row.get('BANCO', ''),
                        orgao=row.get('ORGAO', ''),
                        pmt=pmt,
                        prazo=prazo,
                        tipo_contrato=row.get('TIPO CONTRATO', ''),
                        contrato=row.get('CONTRATO', ''),
                        base_calc=parse_float(row.get('Base Calc', '0')),
                        bruta_5=parse_float(row.get('Bruta 5%', '0')),
                        utilz_5=parse_float(row.get('Utilz 5%', '0')),
                        saldo_5=parse_float(row.get('Saldo 5%', '0')),
                        beneficio_bruta_5=parse_float(row.get('Beneficio Bruta 5%', '0')),
                        beneficio_utilizado_5=parse_float(row.get('Beneficio Utilizado 5%', '0')),
                        beneficio_saldo_5=parse_float(row.get('Beneficio Saldo 5%', '0')),
                        bruta_35=parse_float(row.get('Bruta 35%', '0')),
                        utilz_35=parse_float(row.get('Utilz 35%', '0')),
                        saldo_35=parse_float(row.get('Saldo 35%', '0')),
                        bruta_70=parse_float(row.get('Bruta 70%', '0')),
                        utilz_70=parse_float(row.get('Utilz 70%', '0')),
                        saldo_70=parse_float(row.get('Saldo 70%', '0')),
                        creditos=parse_float(row.get('Créditos', '0')),
                        debitos=parse_float(row.get('Débitos', '0')),
                        liquido=parse_float(row.get('Líquido', '0')),
                        margem=parse_float(row.get('Margem', '0')),
                        exc_soma=parse_float(row.get('EXC Soma', '0')),
                        arq_upag=row.get('ARQ. UPAG', ''),
                        exc_qtd=exc_qtd
                    )
                    debito_add = True

                print(f"Linha {processed_rows} de {total_rows} | Cliente adicionado: {'Sim' if cliente_add else 'Não'} | Débito adicionado: {'Sim' if debito_add else 'Não'}")

            print("Sucesso!")
            return JsonResponse({'status': 'success', 'message': 'Dados importados com sucesso!'}, status=200)

        except Exception as e:
            print(f'Ocorreu um erro ao processar o arquivo CSV: {str(e)}')
            return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro ao processar o arquivo CSV. Detalhes: {str(e)}'}, status=500)

    return render(request, "consultas/gerenciamento.html")
@require_http_methods(["GET", "POST"])
def gerenciamento(request):
    if not request.user.is_authenticated:
        return redirect('usuarios:login')

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        print("Arquivo CSV recebido. Iniciando o processamento...")

        # Headers esperados em diferentes formatos
        expected_headers_sets = [
            [
                "BANCO", "ORGAO", "MATRICULA", "UPAG", "UF", "NOME", "CPF", "RUBRICA", "PMT", "PRAZO",
                "TIPO CONTRATO", "CONTRATO", "Matricula", "Base Calc", "Bruta 5%", "Utilz 5%",
                "Saldo 5%", "Beneficio Bruta 5%", "Beneficio Utilizado 5%", "Beneficio Saldo 5%", "Bruta 35%",
                "Utilz 35%", "Saldo 35%", "Bruta 70%", "Utilz 70%", "Saldo 70%", "Créditos", "Débitos",
                "Líquido", "ARQ. UPAG", "EXC QTD", "EXC Soma", "RJUR", "Sit Func", "Margem"
            ],
            [
                "BANCO", "ORGAO", "MATRICULA", "UPAG", "UF", "NOME", "CPF", "RUBRICA", "PMT", "PRAZO",
                "TIPO CONTRATO", "CONTRATO", "Orgão", "Matricula", "Base Calc", "Bruta 5%", "Utilz 5%",
                "Saldo 5%", "Beneficio Bruta 5%", "Beneficio Utilizado 5%", "Beneficio Saldo 5%", "Bruta 35%",
                "Utilz 35%", "Saldo 35%", "Bruta 70%", "Utilz 70%", "Saldo 70%", "Créditos", "Débitos",
                "Líquido", "ARQ. UPAG", "EXC QTD", "EXC Soma", "RJUR", "Sit Func", "Margem"
            ],
            [
                "BANCO", "ORGAO", "MATRICULA INSTITUIDOR", "MATRICULA", "UPAG", "UF", "NOME", "CPF", "RUBRICA",
                "PMT", "PRAZO", "TIPO CONTRATO", "CONTRATO", "Orgão", "Instituidor", "Matricula", "Base Calc",
                "Bruta 5%", "Utilz 5%", "Saldo 5%", "Beneficio Bruta 5%", "Beneficio Utilizado 5%",
                "Beneficio Saldo 5%", "Bruta 35%", "Utilz 35%", "Saldo 35%", "Bruta 70%", "Utilz 70%", "Saldo 70%",
                "Créditos", "Débitos", "Líquido", "ARQ. UPAG", "EXC QTD", "EXC Soma", "RJUR", "Sit Func", "Margem"
            ]
        ]

        try:
            # Lê o arquivo CSV
            csv_file.seek(0)
            csv_reader = csv.DictReader(csv_file.read().decode('utf-8-sig').splitlines(), delimiter=';', quotechar='"')
            csv_header = csv_reader.fieldnames
            print(f"Headers encontrados: {csv_header}")

            # Verifica se o header do CSV corresponde a algum dos formatos esperados
            matched_headers_set = next((expected_headers_set for expected_headers_set in expected_headers_sets if set(expected_headers_set) <= set(csv_header)), None)
            if not matched_headers_set:
                print("Header do CSV não corresponde a nenhum formato esperado.")
                return JsonResponse({'status': 'error', 'message': 'Header do CSV não corresponde ao formato esperado.'}, status=400)

            print(f"Formato de header correspondente encontrado: {matched_headers_set}")

            expected_fields = matched_headers_set
            missing_fields = [field for field in expected_fields if field not in csv_header]
            if missing_fields:
                print(f"Colunas ausentes no CSV: {missing_fields}")
                return JsonResponse({'status': 'error', 'message': f'Colunas ausentes no CSV: {", ".join(missing_fields)}'}, status=400)

            print("Iniciando o processamento das linhas do CSV...")

            total_rows = sum(1 for _ in csv_reader)
            print(f"Total de linhas no CSV: {total_rows}")

            csv_file.seek(0)
            csv_reader = csv.DictReader(csv_file.read().decode('utf-8-sig').splitlines(), delimiter=';', quotechar='"')

            processed_rows = 0
            for row in csv_reader:
                processed_rows += 1
                cliente_add = False
                debito_add = False

                if any(value == "#N/D" for value in row.values()):
                    print(f"Linha {processed_rows} ignorada devido a '#N/D'")
                    continue

                cpf_normalizado = normalize_cpf(row.get('CPF', ''))
                # print(f"Processando CPF: {cpf_normalizado}")

                try:
                    cliente = Cliente.objects.get(cpf=cpf_normalizado)
                    # print(f"Cliente encontrado: {cliente.nome}")
                except Cliente.DoesNotExist:
                    cliente = Cliente.objects.create(
                        cpf=cpf_normalizado,
                        nome=row.get('NOME', ''),
                        uf=row.get('UF', ''),
                        upag=row.get('UPAG', ''),
                        matricula_instituidor=row.get('MATRICULA INSTITUIDOR', ''),
                        situacao_funcional=row.get('Sit Func', ''),
                        rjur=row.get('RJUR', '')
                    )
                    # print(f"Novo cliente adicionado: {cliente.nome}")
                    cliente_add = True

                pmt = parse_float(row.get('PMT', '0'))
                prazo = row.get('PRAZO', '').strip()
                exc_qtd = int(row.get('EXC QTD', '0').strip() or 0)
                # print(f"PMT: {pmt}, Prazo: {prazo}, EXC QTD: {exc_qtd}")

                all_debitos = MatriculaDebitos.objects.filter(cliente=cliente)
                debitos_same_pmt = all_debitos.filter(pmt=pmt)
                debitos_same_pmt_prazo = debitos_same_pmt.filter(prazo=prazo)
                existing_debitos_dict = {debito.id: debito for debito in debitos_same_pmt_prazo}

                if not existing_debitos_dict:
                    MatriculaDebitos.objects.create(
                        cliente=cliente,
                        matricula=row.get('MATRICULA', ''),
                        rubrica=row.get('RUBRICA', ''),
                        banco=row.get('BANCO', ''),
                        orgao=row.get('ORGAO', ''),
                        pmt=pmt,
                        prazo=prazo,
                        tipo_contrato=row.get('TIPO CONTRATO', ''),
                        contrato=row.get('CONTRATO', ''),
                        base_calc=parse_float(row.get('Base Calc', '0')),
                        bruta_5=parse_float(row.get('Bruta 5%', '0')),
                        utilz_5=parse_float(row.get('Utilz 5%', '0')),
                        saldo_5=parse_float(row.get('Saldo 5%', '0')),
                        beneficio_bruta_5=parse_float(row.get('Beneficio Bruta 5%', '0')),
                        beneficio_utilizado_5=parse_float(row.get('Beneficio Utilizado 5%', '0')),
                        beneficio_saldo_5=parse_float(row.get('Beneficio Saldo 5%', '0')),
                        bruta_35=parse_float(row.get('Bruta 35%', '0')),
                        utilz_35=parse_float(row.get('Utilz 35%', '0')),
                        saldo_35=parse_float(row.get('Saldo 35%', '0')),
                        bruta_70=parse_float(row.get('Bruta 70%', '0')),
                        utilz_70=parse_float(row.get('Utilz 70%', '0')),
                        saldo_70=parse_float(row.get('Saldo 70%', '0')),
                        creditos=parse_float(row.get('Créditos', '0')),
                        debitos=parse_float(row.get('Débitos', '0')),
                        liquido=parse_float(row.get('Líquido', '0')),
                        margem=parse_float(row.get('Margem', '0')),
                        exc_soma=parse_float(row.get('EXC Soma', '0')),
                        arq_upag=row.get('ARQ. UPAG', ''),
                        exc_qtd=exc_qtd
                    )
                    # print(f"Débito adicionado para a linha {processed_rows}")
                    debito_add = True

                print(f"Linha {processed_rows} de {total_rows} | Cliente adicionado: {'Sim' if cliente_add else 'Não'} | Débito adicionado: {'Sim' if debito_add else 'Não'}")

            print("Processamento do CSV concluído com sucesso!")
            return JsonResponse({'status': 'success', 'message': 'Dados importados com sucesso!'}, status=200)

        except Exception as e:
            print(f'Ocorreu um erro ao processar o arquivo CSV: {str(e)}')
            return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro ao processar o arquivo CSV. Detalhes: {str(e)}'}, status=500)

    return render(request, "consultas/gerenciamento.html")