from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.images.edit_handlers import ImageChooserPanel

from streams import blocks


class HomePageCarouselImages(Orderable):
    """Between one and five images for the homepage carousel"""

    page = ParentalKey("home.HomePage", related_name="carousel_images")
    carousel_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,  # the page already exists so this is the default value
        blank=False,  # The field cannot be blank
        on_delete=models.SET_NULL,  # When image is deleted, we don't want anything else to be deleted
        related_name="+",  # Not using a related name
    )

    panels = [
        ImageChooserPanel("carousel_image")
    ]


class HomePage(Page):
    """Home page model"""

    # You can be explicit with where the template is stored
    template = "home/home_page.html"
    # Max count is how many of this type of pages I can have - e.g. only one home page
    max_count = 1

    banner_title = models.CharField(max_length=100, blank=False, null=True)
    banner_subtitle = RichTextField(features=["bold", "italic"])
    banner_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,  # the page already exists so this is the default value
        blank=False,  # The field cannot be blank
        on_delete=models.SET_NULL,  # When image is deleted, we don't want anything else to be deleted
        related_name="+",  # Not using a related name
    )
    banner_cta = models.ForeignKey(
        "wagtailcore.Page",  # Wagtailcore is app name and page is class name
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content = StreamField([("cta", blocks.CTABlock())], null=True, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("banner_title"),
            FieldPanel("banner_subtitle"),
            ImageChooserPanel("banner_image"),
            PageChooserPanel("banner_cta"),
        ], heading="Banner Options"),
        MultiFieldPanel([
            InlinePanel("carousel_images", max_num=5, min_num=1, label="Image"),
        ], heading="Carousel Images"),
        StreamFieldPanel("content"),
    ]

    class Meta:
        verbose_name = "Home Page"
        verbose_name_plural = "Home pages"
