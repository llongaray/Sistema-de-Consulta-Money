from django.core.management.base import BaseCommand
from apps.consultas.models import Cliente, Debito

class Command(BaseCommand):
    help = 'Clear all data in Cliente and Debito tables'

    def handle(self, *args, **kwargs):
        Cliente.objects.all().delete()
        Debito.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully cleared Cliente and Debito tables'))
