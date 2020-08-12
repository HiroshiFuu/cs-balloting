from django.core.management.base import BaseCommand

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

class Command(BaseCommand):
    help = "Init Group"

    # def add_arguments(self, parser):
    #     parser.add_argument('', nargs='+', help='')

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='CompanyUserGroup')
        print(group)
        permissions = ['Can add User', 'Can change User', 'Can delete User', 'Can view User', 'Can add Survey', 'Can change Survey', 'Can delete Survey', 'Can view Survey', 'Can add Survey Option', 'Can change Survey Option', 'Can delete Survey Option', 'Can view Survey Option', 'Can view Survey Result', 'Can view Survey Vote']
        for p_name in permissions:
            permission = Permission.objects.get(name__iexact=p_name)
            print(permission)
            group.permissions.add(permission)