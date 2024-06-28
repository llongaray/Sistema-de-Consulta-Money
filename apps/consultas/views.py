import csv
import logging
from django.shortcuts import render
from django.http import JsonResponse
from .models import Cliente, Debito

# Configurando o logger
logger = logging.getLogger(__name__)

def gerenciamento(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']

        expected_header = [
            "cliente_banco", "cliente_cod_orgao", "cliente_orgao", "cliente_matricula",
            "cliente_upag", "cliente_uf", "cliente_nome", "cliente_cpf", "cliente_valor",
            "cliente_margem", "cliente_margem_cartao", "cliente_prazo", "cliente_situacao"
        ]

        try:
            csv_reader = csv.DictReader(csv_file.read().decode('utf-8-sig').splitlines(), delimiter=';', quotechar='"')
            csv_header = csv_reader.fieldnames

            if csv_header != expected_header:
                return JsonResponse({'status': 'error', 'message': f'O cabeçalho do CSV deve ser igual a: {";".join(expected_header)}'}, status=400)

            for row in csv_reader:
                # Atualiza ou cria o cliente com base no CPF
                cliente, created = Cliente.objects.update_or_create(
                    cpf_cliente=row['cliente_cpf'],
                    defaults={
                        'nome_cliente': row['cliente_nome'],
                        'uf_cliente': row['cliente_uf'],
                        'cidade_cliente': '',
                        'telefone_cliente': '',
                        'idade_cliente': None
                    }
                )

                # Verifica se já existe um débito para o cliente com o mesmo valor e prazo
                try:
                    Debito.objects.get(
                        cliente=cliente,
                        valor_cliente=float(row['cliente_valor']),
                        prazo_cliente=int(row['cliente_prazo'])
                    )
                except Debito.DoesNotExist:
                    # Cria um novo débito para o cliente
                    Debito.objects.create(
                        cliente=cliente,
                        matricula_cliente=row['cliente_matricula'],
                        upag_cliente=row['cliente_upag'],
                        banco_cliente=row['cliente_banco'],
                        cod_orgao_cliente=row['cliente_cod_orgao'],
                        desc_cod_orgao_cliente=row['cliente_orgao'],  # Atualiza o campo desc_cod_orgao_cliente com cliente_orgao do CSV
                        valor_cliente=float(row['cliente_valor']),
                        margem_cliente=float(row['cliente_margem']),
                        margem_cartao_cliente=float(row['cliente_margem_cartao']),
                        prazo_cliente=int(row['cliente_prazo']),
                        situacao_cliente=row['cliente_situacao']
                    )

            return JsonResponse({'status': 'success', 'message': 'Dados importados com sucesso!'}, status=200)

        except Exception as e:
            logger.error(f'Ocorreu um erro ao processar o arquivo CSV: {str(e)}')
            return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro ao processar o arquivo CSV. Detalhes: {str(e)}'}, status=500)

    return render(request, "consultas/index.html")
