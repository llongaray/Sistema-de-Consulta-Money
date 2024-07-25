from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Clear all data in Ranking and RegisterMoney tables'

    def handle(self, *args, **kwargs):
        try:
            # Importa os modelos dentro do método para evitar importação circular
            from apps.funcionarios.models import Ranking, RegisterMoney

            # Limpa todos os registros de Ranking
            Ranking.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully cleared Ranking table'))

            # Limpa todos os registros de RegisterMoney
            RegisterMoney.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully cleared RegisterMoney table'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to clear tables: {str(e)}'))
