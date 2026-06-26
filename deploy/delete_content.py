from content.models import Episode, Show, Teaser, EpisodeAnalytics
from interactions.models import EpisodeHit, Comment, Like, Favorite, Report

print("Deleting EpisodeAnalytics...")
print(EpisodeAnalytics.objects.all().delete())
print("Deleting EpisodeHits...")
print(EpisodeHit.objects.all().delete())
print("Deleting Comments...")
print(Comment.objects.all().delete())
print("Deleting Likes...")
print(Like.objects.all().delete())
print("Deleting Favorites...")
print(Favorite.objects.all().delete())
print("Deleting Reports...")
print(Report.objects.all().delete())
print("Deleting Teasers...")
print(Teaser.objects.all().delete())
print("Deleting Episodes...")
print(Episode.objects.all().delete())
print("Deleting Shows...")
print(Show.objects.all().delete())

from content.models import Category, Author
print("Categories remaining:", Category.objects.count())
print("Authors remaining:", Author.objects.count())
