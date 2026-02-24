from django.contrib.sitemaps import Sitemap

from .models import Article

class BlogSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.5

    def items(self):
        return (
            Article.objects
            .filter(published_date__isnull=False)
            .order_by("-published_date")[:5]
        )

    def lastmod(self, obj):
        return obj.published_date

