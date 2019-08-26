from django.db import models

from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel


class HomePage(Page):
    """Home page model"""
    templates = "home/templates/home_page.html"
    banner_title = models.CharField(max_length=100, blank=False, null=True)
    max_count = 1
    content_panels = Page.content_panels + [
        FieldPanel("banner_title")
    ]

    class Meta:
        verbose_name = "Home Page"
        verbose_name_plural = "Home pages"
