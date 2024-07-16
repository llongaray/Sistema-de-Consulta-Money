from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Cliente, MatriculaDebitos
import csv
import logging
from django.db import transaction
import time
from datetime import timedelta
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required


# Configurando o logger
logger = logging.getLogger(__name__)

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

def ficha_cliente(request, cpf):
    cliente = get_object_or_404(Cliente, cpf=cpf)
    matriculas_db = MatriculaDebitos.objects.filter(cliente=cliente)
    
    margens = []  # Lista para armazenar as margens
    first_margem = 0  # Variável para controlar a primeira inserção
    
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
        
        # Verifica duplicidade apenas após a primeira inserção
        if first_margem > 0:
            print('first é: ' + str(first_margem))
            if matricula.saldo_35 not in margens:
                margens.append({
                    'saldo_35': matricula.saldo_35,
                    'saldo_5': matricula.saldo_5,
                    'beneficio_saldo_5': matricula.beneficio_saldo_5,
                })
        else:
            print('first é 0')
            margens.append({
                'saldo_35': matricula.saldo_35,
                'saldo_5': matricula.saldo_5,
                'beneficio_saldo_5': matricula.beneficio_saldo_5,
            })
            print("saldo_35: " + str(matricula.saldo_35))
            print("saldo_5: " + str(matricula.saldo_5))
            print("beneficio_saldo_5: " + str(matricula.beneficio_saldo_5))
            first_margem += 1
    
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
        'margens': margens,  # Passa a lista de margens ao contexto
        'matriculas': matriculas,  # Adiciona a lista de matrículas ao contexto
    }
    print("fim ficha")
    return render(request, 'consultas/ficha_cliente.html', context)

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
    print("Gerenciamento.......")

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        expected_fields = [
            "BANCO", "ORGAO", "MATRICULA", "UPAG", "UF", "NOME", "CPF", "RUBRICA", "PMT", "PRAZO",
            "TIPO CONTRATO", "CONTRATO", "Orgão", "Matricula", "Base Calc", "Bruta 5%", "Utilz 5%",
            "Saldo 5%", "Beneficio Bruta 5%", "Beneficio Utilizado 5%", "Beneficio Saldo 5%", "Bruta 35%",
            "Utilz 35%", "Saldo 35%", "Bruta 70%", "Utilz 70%", "Saldo 70%", "Créditos", "Débitos",
            "Líquido", "ARQ. UPAG", "EXC QTD", "EXC Soma", "RJUR", "Sit Func", "Margem"
        ]

        try:

            # Contar o número total de linhas no CSV
            csv_reader = csv.DictReader(csv_file.read().decode('utf-8-sig').splitlines(), delimiter=';', quotechar='"')
            total_rows = sum(1 for row in csv_reader)
            csv_file.seek(0)  # Voltar o ponteiro do arquivo para o início

            csv_reader = csv.DictReader(csv_file.read().decode('utf-8-sig').splitlines(), delimiter=';', quotechar='"')
            csv_header = csv_reader.fieldnames

            missing_fields = [field for field in expected_fields if field not in csv_header]
            if missing_fields:
                return JsonResponse({'status': 'error', 'message': f'Colunas ausentes no CSV: {", ".join(missing_fields)}'}, status=400)

            processed_rows = 0
            print("iniciando for......")
            for row in csv_reader:
                processed_rows += 1
                print('linha: ' + str(processed_rows))
                # Verifica se o cliente já existe pelo CPF
                cpf_normalizado = normalize_cpf(row['CPF'])
                cliente, created = Cliente.objects.get_or_create(
                    cpf=cpf_normalizado,
                    defaults={
                        'nome': row['NOME'],
                        'uf': row['UF'],
                        'upag': row['UPAG'],
                        'matricula_instituidor': row.get('MATRICULA INSTITUIDOR', ''),
                        'situacao_funcional': row['Sit Func'],
                        'rjur': row['RJUR']
                    }
                )
                # Convertendo os campos para float, verificando se não estão vazios
                pmt = parse_float(row['PMT'])
                base_calc = parse_float(row['Base Calc'])
                bruta_5 = parse_float(row['Bruta 5%'])
                utilz_5 = parse_float(row['Utilz 5%'])
                saldo_5 = parse_float(row['Saldo 5%'])
                beneficio_bruta_5 = parse_float(row['Beneficio Bruta 5%'])
                beneficio_utilizado_5 = parse_float(row['Beneficio Utilizado 5%'])
                beneficio_saldo_5 = parse_float(row['Beneficio Saldo 5%'])
                bruta_35 = parse_float(row['Bruta 35%'])
                utilz_35 = parse_float(row['Utilz 35%'])
                saldo_35 = parse_float(row['Saldo 35%'])
                bruta_70 = parse_float(row['Bruta 70%'])
                utilz_70 = parse_float(row['Utilz 70%'])
                saldo_70 = parse_float(row['Saldo 70%'])
                creditos = parse_float(row['Créditos'])
                debitos = parse_float(row['Débitos'])
                liquido = parse_float(row['Líquido'])
                margem = parse_float(row['Margem'])
                exc_soma = parse_float(row['EXC Soma'])
                prazo = row['PRAZO'].strip()
                if 'EXC QTD' in row:
                    exc_qtd = int(row['EXC QTD']) if row['EXC QTD'].strip() else 0
                else:
                    exc_qtd = 0

                # Verifica se já existe um débito com as mesmas informações de BANCO, PMT e PRAZO
                existing_debito = MatriculaDebitos.objects.filter(
                    cliente=cliente,
                    banco=row['BANCO'],
                    pmt=pmt,
                    prazo=prazo
                ).exists()
                # print("debito filtrado")
                if not existing_debito: 
                    # Cria o débito para o cliente
                    MatriculaDebitos.objects.create(
                        cliente=cliente,
                        matricula=row['MATRICULA'],
                        rubrica=row['RUBRICA'],
                        banco=row['BANCO'],
                        orgao=row['ORGAO'],
                        pmt=pmt,
                        prazo=prazo,
                        tipo_contrato=row['TIPO CONTRATO'],
                        contrato=row['CONTRATO'],
                        base_calc=parse_float(row['Base Calc']),
                        bruta_5=parse_float(row['Bruta 5%']),
                        utilz_5=parse_float(row['Utilz 5%']),
                        saldo_5=parse_float(row['Saldo 5%']),
                        beneficio_bruta_5=parse_float(row['Beneficio Bruta 5%']),
                        beneficio_utilizado_5=parse_float(row['Beneficio Utilizado 5%']),
                        beneficio_saldo_5=parse_float(row['Beneficio Saldo 5%']),
                        bruta_35=parse_float(row['Bruta 35%']),
                        utilz_35=parse_float(row['Utilz 35%']),
                        saldo_35=parse_float(row['Saldo 35%']),
                        bruta_70=parse_float(row['Bruta 70%']),
                        utilz_70=parse_float(row['Utilz 70%']),
                        saldo_70=parse_float(row['Saldo 70%']),
                        creditos=parse_float(row['Créditos']),
                        debitos=parse_float(row['Débitos']),
                        liquido=parse_float(row['Líquido']),
                        margem = parse_float(row['Margem']),
                        exc_soma = parse_float(row['EXC Soma']),
                        arq_upag=row.get('ARQ. UPAG', ''),
                        exc_qtd=exc_qtd
                    )
                    
            print("Sucesso!")
            return JsonResponse({'status': 'success', 'message': 'Dados importados com sucesso!'}, status=200)

        except Exception as e:
            print(f'Ocorreu um erro ao processar o arquivo CSV: {str(e)}')
            return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro ao processar o arquivo CSV. Detalhes: {str(e)}'}, status=500)

    return render(request, "consultas/gerenciamento.html")