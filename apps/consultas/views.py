from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Cliente, MatriculaDebitos
import csv
import logging
from django.db import transaction
from decimal import Decimal, InvalidOperation

# Configurando o logger
logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def consulta_cliente(request):
    cpf_cliente = request.GET.get('cpf_cliente', None)
    
    if cpf_cliente:
        try:
            cliente = Cliente.objects.get(cpf=cpf_cliente)
            return redirect('consulta:ficha_cliente_cpf', cpf_cliente=cpf_cliente)  # Nome do argumento corrigido
        except Cliente.DoesNotExist:
            return JsonResponse({'error': 'Cliente não encontrado'}, status=404)
    else:
        return render(request, 'consultas/consulta_cliente.html')

def ficha_cliente(request, cpf_cliente):
    cliente = Cliente.objects.get(cpf=cpf_cliente)  # Ajuste o nome do argumento aqui também
    matriculas_debitos = MatriculaDebitos.objects.filter(cliente=cliente).order_by('matricula', 'debito')
    
    context = {
        'cliente': cliente,
        'matriculas_debitos': matriculas_debitos,
    }
    return render(request, 'consultas/ficha_cliente.html', context)

@require_http_methods(["GET", "POST"])
def gerenciamento(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']

        expected_fields = [
            "BANCO", "ORGAO", "MATRICULA INSTITUIDOR", "MATRICULA", "UPAG", "UF", "NOME", "CPF", "RUBRICA", "PMT", "PRAZO",
            "TIPO CONTRATO", "CONTRATO", "Instituidor", "Matricula", "Base Calc", "Bruta 5%", "Utilz 5%",
            "Saldo 5%", "Beneficio Bruta 5%", "Beneficio Utilizado 5%", "Beneficio Saldo 5%", "Bruta 35%",
            "Utilz 35%", "Saldo 35%", "Bruta 70%", "Utilz 70%", "Saldo 70%", "Créditos", "Débitos",
            "Líquido", "EXC Soma", "RJUR", "Sit Func", "Margem"
        ]

        try:
            csv_reader = csv.DictReader(csv_file.read().decode('utf-8-sig').splitlines(), delimiter=';', quotechar='"')
            csv_header = csv_reader.fieldnames

            missing_fields = [field for field in expected_fields if field not in csv_header]
            if missing_fields:
                return JsonResponse({'status': 'error', 'message': f'Colunas ausentes no CSV: {", ".join(missing_fields)}'}, status=400)

            for row in csv_reader:
                # Verifica se o cliente já existe pelo CPF
                cliente, created = Cliente.objects.get_or_create(
                    cpf=row['CPF'],
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
                try:
                    pmt = "{:.2f}".format(float(row['PMT'].replace('.', '').replace(',', '.'))) if row['PMT'].strip() else "0.00"
                except ValueError:
                    pmt = "0.00"

                try:
                    base_calc = "{:.2f}".format(float(row['Base Calc'].replace('.', '').replace(',', '.'))) if row['Base Calc'].strip() else "0.00"
                except ValueError:
                    base_calc = "0.00"

                try:
                    bruta_5 = "{:.2f}".format(float(row['Bruta 5%'].replace('.', '').replace(',', '.'))) if row['Bruta 5%'].strip() else "0.00"
                except ValueError:
                    bruta_5 = "0.00"

                try:
                    utilz_5 = "{:.2f}".format(float(row['Utilz 5%'].replace('.', '').replace(',', '.'))) if row['Utilz 5%'].strip() else "0.00"
                except ValueError:
                    utilz_5 = "0.00"

                try:
                    saldo_5 = "{:.2f}".format(float(row['Saldo 5%'].replace('.', '').replace(',', '.'))) if row['Saldo 5%'].strip() else "0.00"
                except ValueError:
                    saldo_5 = "0.00"

                try:
                    beneficio_bruta_5 = "{:.2f}".format(float(row['Beneficio Bruta 5%'].replace('.', '').replace(',', '.'))) if row['Beneficio Bruta 5%'].strip() else "0.00"
                except ValueError:
                    beneficio_bruta_5 = "0.00"

                try:
                    beneficio_utilizado_5 = "{:.2f}".format(float(row['Beneficio Utilizado 5%'].replace('.', '').replace(',', '.'))) if row['Beneficio Utilizado 5%'].strip() else "0.00"
                except ValueError:
                    beneficio_utilizado_5 = "0.00"

                try:
                    beneficio_saldo_5 = "{:.2f}".format(float(row['Beneficio Saldo 5%'].replace('.', '').replace(',', '.'))) if row['Beneficio Saldo 5%'].strip() else "0.00"
                except ValueError:
                    beneficio_saldo_5 = "0.00"

                try:
                    bruta_35 = "{:.2f}".format(float(row['Bruta 35%'].replace('.', '').replace(',', '.'))) if row['Bruta 35%'].strip() else "0.00"
                except ValueError:
                    bruta_35 = "0.00"

                try:
                    utilz_35 = "{:.2f}".format(float(row['Utilz 35%'].replace('.', '').replace(',', '.'))) if row['Utilz 35%'].strip() else "0.00"
                except ValueError:
                    utilz_35 = "0.00"

                try:
                    saldo_35 = "{:.2f}".format(float(row['Saldo 35%'].replace('.', '').replace(',', '.'))) if row['Saldo 35%'].strip() else "0.00"
                except ValueError:
                    saldo_35 = "0.00"

                try:
                    bruta_70 = "{:.2f}".format(float(row['Bruta 70%'].replace('.', '').replace(',', '.'))) if row['Bruta 70%'].strip() else "0.00"
                except ValueError:
                    bruta_70 = "0.00"

                try:
                    utilz_70 = "{:.2f}".format(float(row['Utilz 70%'].replace('.', '').replace(',', '.'))) if row['Utilz 70%'].strip() else "0.00"
                except ValueError:
                    utilz_70 = "0.00"

                try:
                    saldo_70 = "{:.2f}".format(float(row['Saldo 70%'].replace('.', '').replace(',', '.'))) if row['Saldo 70%'].strip() else "0.00"
                except ValueError:
                    saldo_70 = "0.00"

                try:
                    creditos = "{:.2f}".format(float(row['Créditos'].replace('.', '').replace(',', '.'))) if row['Créditos'].strip() else "0.00"
                except ValueError:
                    creditos = "0.00"

                try:
                    debitos = "{:.2f}".format(float(row['Débitos'].replace('.', '').replace(',', '.'))) if row['Débitos'].strip() else "0.00"
                except ValueError:
                    debitos = "0.00"

                try:
                    liquido = "{:.2f}".format(float(row['Líquido'].replace('.', '').replace(',', '.'))) if row['Líquido'].strip() else "0.00"
                except ValueError:
                    liquido = "0.00"

                try:
                    exc_soma = "{:.2f}".format(float(row['EXC Soma'].replace('.', '').replace(',', '.'))) if row['EXC Soma'].strip() else "0.00"
                except ValueError:
                    exc_soma = "0.00"

                # Verifica se já existe um débito com as mesmas informações
                existing_debito = MatriculaDebitos.objects.filter(
                    cliente=cliente,
                    matricula=row['MATRICULA'],
                    banco=row['BANCO'],
                    saldo_5=saldo_5,
                    beneficio_saldo_5=beneficio_saldo_5,
                    saldo_35=saldo_35,
                    saldo_70=saldo_70
                ).exists()

                if not existing_debito:
                    # Cria o débito para o cliente
                    MatriculaDebitos.objects.create(
                        cliente=cliente,
                        matricula=row['MATRICULA'],
                        debito=row['RUBRICA'],
                        banco=row['BANCO'],
                        orgao=row['ORGAO'],
                        pmt=pmt,
                        prazo=int(row['PRAZO']),
                        tipo_contrato=row['TIPO CONTRATO'],
                        contrato=row['CONTRATO'],
                        base_calc=base_calc,
                        bruta_5=bruta_5,
                        utilz_5=utilz_5,
                        saldo_5=saldo_5,
                        beneficio_bruta_5=beneficio_bruta_5,
                        beneficio_utilizado_5=beneficio_utilizado_5,
                        beneficio_saldo_5=beneficio_saldo_5,
                        bruta_35=bruta_35,
                        utilz_35=utilz_35,
                        saldo_35=saldo_35,
                        bruta_70=bruta_70,
                        utilz_70=utilz_70,
                        saldo_70=saldo_70,
                        creditos=creditos,
                        debitos=debitos,
                        liquido=liquido,
                        exc_soma=exc_soma,
                        arq_upag=row.get('Arq. UPAG', ''),
                        exc_qtd=int(row['EXC Qtd']) if 'EXC Qtd' in row else 0
                    )

            return JsonResponse({'status': 'success', 'message': 'Dados importados com sucesso!'}, status=200)

        except Exception as e:
            logger.error(f'Ocorreu um erro ao processar o arquivo CSV: {str(e)}')
            return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro ao processar o arquivo CSV. Detalhes: {str(e)}'}, status=500)

    return render(request, "consultas/gerenciamento.html")