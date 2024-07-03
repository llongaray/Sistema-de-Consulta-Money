from django.core.management.base import BaseCommand
from apps.consultas.models import Cliente, MatriculaDebitos

class Command(BaseCommand):
    help = 'Clear all data in Cliente and MatriculaDebitos tables'

    def handle(self, *args, **kwargs):
        try:
            # Limpa todos os registros de Cliente
            Cliente.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully cleared Cliente table'))

            # Limpa todos os registros de MatriculaDebitos
            MatriculaDebitos.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully cleared MatriculaDebitos table'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to clear tables: {str(e)}'))

