from django.core.management.base import BaseCommand
from django.core.management import call_command
from content.models import Episode, Show, Language, Category
from accounts.models import CustomUser


class Command(BaseCommand):
    help = "Delete all episodes/shows/languages/categories + unblock all users"

    def handle(self, *args, **options):
        # 1. Delete episodes
        count = Episode.objects.all().delete()[0]
        self.stdout.write(self.style.SUCCESS(f"Episodes deleted: {count}"))

        # 2. Delete shows
        count = Show.objects.all().delete()[0]
        self.stdout.write(self.style.SUCCESS(f"Shows deleted: {count}"))

        # 3. Delete languages
        count = Language.objects.all().delete()[0]
        self.stdout.write(self.style.SUCCESS(f"Languages deleted: {count}"))

        # 4. Delete categories
        count = Category.objects.all().delete()[0]
        self.stdout.write(self.style.SUCCESS(f"Categories deleted: {count}"))

        # 5. Re-seed default languages (English, Hindi, GenZ)
        call_command('seed_languages')
        self.stdout.write(self.style.SUCCESS("Default languages re-seeded"))

        # 6. Unblock all users
        blocked = CustomUser.objects.filter(is_active=False)
        count = blocked.count()
        blocked.update(is_active=True)
        self.stdout.write(self.style.SUCCESS(f"Users unblocked: {count}"))

        # 7. Summary
        total = CustomUser.objects.count()
        active = CustomUser.objects.filter(is_active=True).count()
        self.stdout.write(self.style.SUCCESS(f"\nTotal users: {total} | Active: {active}"))
        self.stdout.write(self.style.SUCCESS("✅ Done!"))
