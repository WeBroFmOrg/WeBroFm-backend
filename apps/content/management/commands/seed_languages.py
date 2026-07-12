from django.core.management.base import BaseCommand
from content.models import Language

LANGUAGES = [
    {"name": "English", "code": "en"},
    {"name": "Hindi", "code": "hi"},
    {"name": "GenZ", "code": "genz"},
]


class Command(BaseCommand):
    help = "Seed default languages (English, Hindi, GenZ)"

    def handle(self, *args, **options):
        created = 0
        for data in LANGUAGES:
            _, is_new = Language.objects.get_or_create(
                code=data["code"],
                defaults=data
            )
            if is_new:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {data['name']}"))
            else:
                self.stdout.write(f"Exists: {data['name']}")

        self.stdout.write(self.style.SUCCESS(f"\nDone! {created} languages created, {len(LANGUAGES) - created} already exist."))
