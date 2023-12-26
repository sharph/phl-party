from django.core.management.base import BaseCommand, CommandError
from legistar.parse_legislation_detail import get_legislation
from legistar.models import import_legislation


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("id", type=int)
        parser.add_argument("guid", type=str)

    def handle(self, *args, **options):
        legislation = get_legislation(options["id"], options["guid"])
        print(import_legislation(legislation, int(options["id"]), options["guid"]))
