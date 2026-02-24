from django.contrib.syndication.views import Feed
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView

from blogapp.models import Article


# Create your views here.
class ArticlesListView(ListView):
    model = Article
    queryset = (
        Article.objects
        .filter(published_date__isnull=False)
        .order_by("-published_date")
    )


class ArticlesDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates or change and addition blog articles"
    link = reverse_lazy("blogapp:articles")

    def items(self):
        return (
        Article.objects
        .filter(published_date__isnull=False)
        .order_by("-published_date")[:5]
    )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.body[:200]
