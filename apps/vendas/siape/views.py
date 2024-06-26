from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from apps.consultas.models import Cliente, Debito

@require_http_methods(["GET"])  # Aceita apenas requisições GET
def consulta_cliente(request):
    cpf_cliente = request.GET.get('cpf_cliente', None)
    
    if cpf_cliente:
        try:
            cliente = Cliente.objects.get(cpf_cliente=cpf_cliente)
            # Se o cliente existe, redireciona para a página de ficha_cliente
            return redirect('siape:ficha_cliente_cpf', cpf_cliente=cpf_cliente)
        except Cliente.DoesNotExist:
            return JsonResponse({'error': 'Cliente não encontrado'}, status=404)
    else:
        # Se não houver cpf_cliente na requisição, renderiza o template consulta_cliente.html
        return render(request, 'vendas/consulta_cliente.html')

def ficha_cliente(request, cpf_cliente=None):
    if request.method == 'GET':
        if cpf_cliente:
            # Busca o cliente pelo CPF
            cliente = get_object_or_404(Cliente, cpf_cliente=cpf_cliente)
            
            # Busca os débitos associados ao cliente pelo id
            debitos = Debito.objects.filter(cliente_id=cliente.id)
            
            # Contexto com informações do cliente
            context_info = {
                'cpf_cliente': cliente.cpf_cliente,
                'nome_cliente': cliente.nome_cliente,
                'uf_cliente': cliente.uf_cliente,
                'cidade_cliente': cliente.cidade_cliente,
                'telefone_cliente': cliente.telefone_cliente,
                'idade_cliente': cliente.idade_cliente,
            }
            
            # Contexto com débitos associados ao cliente
            context_debitos = []
            for debito in debitos:
                context_debito = {
                    'cliente_id': debito.cliente_id,
                    'matricula_cliente': debito.matricula_cliente,
                    'upag_cliente': debito.upag_cliente,
                    'banco_cliente': debito.banco_cliente,
                    'cod_orgao_cliente': debito.cod_orgao_cliente,
                    'desc_cod_orgao_cliente': debito.desc_cod_orgao_cliente,
                    'valor_cliente': debito.valor_cliente,
                    'margem_cartao_cliente': debito.margem_cartao_cliente,
                    'prazo_cliente': debito.prazo_cliente,
                    'situacao_cliente': debito.situacao_cliente,
                }
                context_debitos.append(context_debito)
            
            # Combinando ambos os contextos em um único contexto
            context = {
                'context_info': context_info,
                'context_debitos': context_debitos,
            }
            
            return render(request, 'vendas/ficha_cliente.html', context)
        else:
            return JsonResponse({'error': 'CPF do cliente não fornecido'}, status=400)

