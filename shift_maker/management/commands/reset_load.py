from ...models import User
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help="Userのworkloadを０にするコマンド"

    def handle(self, *args, **options):
        users=User.objects.filter(Block_name=options["Block_name"])
        for user in users:
            user.workload_sum = 0
        User.objects.bulk_update(users,fields=["workload_sum"])

    def add_arguments(self,parser):
        parser.add_argument("--Block_name",nargs="?",default="",type=str)