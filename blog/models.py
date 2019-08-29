from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.shortcuts import render

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel,
    MultiFieldPanel,
    InlinePanel,
)
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.snippets.models import register_snippet

from streams import blocks


class BlogAuthorsOrderable(Orderable):
    """This allows us to select one or more blog authors from snippets"""

    page = ParentalKey("blog.BlogDetailPage", related_name="blog_authors")
    author = models.ForeignKey("blog.BlogAuthor", on_delete=models.CASCADE)

    panels = [SnippetChooserPanel("author")]


class BlogAuthor(models.Model):
    """Blog author for snippets."""

    name = models.CharField(max_length=100)
    website = models.URLField(blank=True, null=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="+",
    )
    panels = [
        MultiFieldPanel(
            [FieldPanel("name"), ImageChooserPanel("image")],
            heading="Name and Image",
        ),
        MultiFieldPanel([FieldPanel("website")], heading="Links"),
    ]

    def __str__(self):
        """str repr of this class"""
        return self.name

    class Meta:  # noqa
        verbose_name = "Blog Author"
        verbose_name_plural = "Blog Authors"


register_snippet(BlogAuthor)


class BlogCategory(models.Model):
    """Blog category for a snippet."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(
        verbose_name="slug",
        allow_unicode=True,
        max_length=255,
        help_text="A slug to identify posts by this category",
    )

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name

    class Meta:  # noqa
        verbose_name = "Blog category"
        verbose_name_plural = "Blog categories"
        ordering = ["name"]


register_snippet(BlogCategory)


class BlogListingPage(RoutablePageMixin, Page):
    """Listing page lists all the Blog Detail Pags"""

    # Getting all the blog detail pages and putting them into this page
    template = "blog/blog_listing_page.html"

    custom_title = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        help_text="Overwrites the default title",
    )

    content_panels = Page.content_panels + [FieldPanel("custom_title")]

    def get_context(self, request, *args, **kwargs):
        """Adding custom stuff to our context."""
        context = super().get_context(request)
        all_posts = (
            BlogDetailPage.objects.live()
            .public()
            .order_by("-first_published_at")
        )
        # Adding paginator to blog listing page:
        paginator = Paginator(all_posts, 3)  # todo change to five per page
        page = request.GET.get("page")
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)


        context["posts"] = posts
        # This gives the reverse of latest blog subpage
        context["special_link"] = self.reverse_subpage("latest_blog_posts")
        context["categories"] = BlogCategory.objects.all

        # If there is a get request on category name, return posts from just that category
        if (
            BlogDetailPage.objects.live()
            .public()
            .filter(categories__slug__in=[request.GET.get("category")])
        ):
            context["posts"] = (
                BlogDetailPage.objects.live()
                .public()
                .filter(categories__slug__in=[request.GET.get("category")])
            )
        return context

    @route(r"^latest/$")
    def latest_blog_posts(self, request, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)
        # Could create a new context for latest posts
        context["latest_posts"] = BlogDetailPage.objects.live().public()[:1]
        # Or change the context to show only the last x post(s)
        context["posts"] = context["posts"][:3]
        return render(request, "blog/latest_posts.html", context)

    def get_sitemap_urls(self, request):
        # Uncomment to have no sitemap for this page
        # return []
        sitemap = super().get_sitemap_urls(request)
        sitemap.append(
            {
                "location": self.full_url
                + self.reverse_subpage("latest_blog_posts"),
                "lastmod": (
                    self.last_published_at or self.latest_revision_created_at
                ),
                "priority": 0.9,
            }
        )
        return sitemap


class BlogDetailPage(Page):
    """Parental Blog Detail Page."""

    custom_title = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        help_text="Overwrites the default title",
    )

    description = RichTextField(features=[], blank=True, null=True)

    banner_image = models.ForeignKey(
        "wagtailimages.Image",
        blank=False,
        null=True,
        related_name="+",
        on_delete="models.SET_NULL",
    )
    content = StreamField(
        [
            ("title_and_text", blocks.TitleAndTextBlock()),
            ("full_richtext", blocks.RichTextBlock()),
            ("simple_richtext", blocks.SimpleRichTextBlock()),
            ("cards", blocks.CardBlock()),
            ("cta", blocks.CTABlock()),
        ],
        null=True,
        blank=True,
    )

    categories = ParentalManyToManyField("blog.BlogCategory", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("custom_title"),
        ImageChooserPanel("banner_image"),
        FieldPanel("description"),
        MultiFieldPanel(
            [
                InlinePanel(
                    "blog_authors", label="Author", min_num=1, max_num=10
                )
            ],
            heading="Author(s)",
        ),
        MultiFieldPanel(
            [FieldPanel("categories", widget=forms.CheckboxSelectMultiple)],
            heading="Categories",
        ),
        StreamFieldPanel("content"),
    ]


# First subclassed blog post page


class ArticleBlogPage(BlogDetailPage):
    """A subclassed blog post page for articles"""

    template = "blog/article_blog_page.html"

    subtitle = models.CharField(max_length=100, blank=True, null=True)

    intro_image = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Best size for this immage will be 200x400",
    )

    content_panels = Page.content_panels + [
        FieldPanel("custom_title"),
        FieldPanel("subtitle"),
        ImageChooserPanel("intro_image"),
        ImageChooserPanel("banner_image"),
        FieldPanel("description"),
        MultiFieldPanel(
            [
                InlinePanel(
                    "blog_authors", label="Author", min_num=1, max_num=10
                )
            ],
            heading="Author(s)",
        ),
        MultiFieldPanel(
            [FieldPanel("categories", widget=forms.CheckboxSelectMultiple)],
            heading="Categories",
        ),
        StreamFieldPanel("content"),
    ]


class VideoBlogPage(BlogDetailPage):
    """Video subclassed page"""

    template = "blog/video_blog_page.html"

    youtube_video_id = models.CharField(max_length=50)

    content_panels = Page.content_panels + [
        FieldPanel("custom_title"),
        ImageChooserPanel("banner_image"),
        FieldPanel("description"),
        MultiFieldPanel(
            [
                InlinePanel(
                    "blog_authors", label="Author", min_num=1, max_num=10
                )
            ],
            heading="Author(s)",
        ),
        MultiFieldPanel(
            [FieldPanel("categories", widget=forms.CheckboxSelectMultiple)],
            heading="Categories",
        ),
        FieldPanel("youtube_video_id"),
        StreamFieldPanel("content"),
    ]
