from django.core.management.base import BaseCommand
from content.models import Episode
from services.hls_converter import convert_episode_to_hls

class Command(BaseCommand):
    help = 'Converts episodes without HLS playlists to HLS format'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Re-convert even if HLS already exists')
        parser.add_argument('--id', type=int, help='Convert a specific episode ID')

    def handle(self, *args, **options):
        if options['id']:
            episodes = Episode.objects.filter(id=options['id'])
        elif options['force']:
            episodes = Episode.objects.all()
        else:
            episodes = Episode.objects.filter(hls_playlist_key='')

        count = episodes.count()
        self.stdout.write(self.style.SUCCESS(f'Found {count} episodes to process'))

        for ep in episodes:
            self.stdout.write(f'Processing Episode {ep.id}: {ep.title}...')
            success = convert_episode_to_hls(ep)
            if success:
                self.stdout.write(self.style.SUCCESS(f'Successfully converted {ep.title}'))
            else:
                self.stdout.write(self.style.ERROR(f'Failed to convert {ep.title}'))
