from django.core.management.base import BaseCommand, CommandError
from legistar.parse_legislation_detail import (
    get_legislation,
    get_ids_guids,
)
from legistar.models import import_legislation, Legislation
import time


class Command(BaseCommand):
    help = "Imports items from RSS"

    def add_arguments(self, parser):
        parser.add_argument("--repeat-seconds", type=int, default=None, required=False)

    def handle(self, *args, **options):
        start_time = time.time()
        while True:
            ids_guids = get_ids_guids()
            print(len(ids_guids), "items")
            for legistar_id, guid in ids_guids:
                try:
                    legislation_obj = Legislation.objects.get(
                        legistar_id=legistar_id, legistar_guid=guid
                    )
                    if legislation_obj.final_action:
                        print(
                            legislation_obj.file_number, "has final action. Not fetching!"
                        )
                        continue
                except Legislation.DoesNotExist:
                    pass
                legislation = get_legislation(legistar_id, guid)
                try:
                    print(import_legislation(legislation, legistar_id, guid))
                except Exception as exc:
                    print(exc)
            if options["repeat_seconds"]:
                print("Pausing")
                while time.time() - start_time < options["repeat_seconds"]:
                    time.sleep(1)
                print("Resuming")
            else:
                break
