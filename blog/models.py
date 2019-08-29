from django.db import models
from django.shortcuts import render

from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel,
    MultiFieldPanel,
)
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.snippets.models import register_snippet

from streams import blocks


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
        context["posts"] = BlogDetailPage.objects.live().public()
        # This gives the reverse of latest blog subpage
        context["special_link"] = self.reverse_subpage("latest_blog_posts")
        return context

    @route(r"^latest/$")
    def latest_blog_posts(self, request, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)
        # Could create a new context for latest posts
        context["latest_posts"] = BlogDetailPage.objects.live().public()[:1]
        # Or change the context to show only the last x post(s)
        context["posts"] = context["posts"][:1]
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
    """Blog Detail Page"""

    custom_title = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        help_text="Overwrites the default title",
    )

    description = RichTextField(
        features=[], blank=True, null=True
    )

    blog_image = models.ForeignKey(
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
    content_panels = Page.content_panels + [
        FieldPanel("custom_title"),
        ImageChooserPanel("blog_image"),
        FieldPanel("description"),
        StreamFieldPanel("content"),
    ]
