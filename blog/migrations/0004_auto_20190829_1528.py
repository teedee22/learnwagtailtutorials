# Generated by Django 2.2.4 on 2019-08-29 15:28

from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_blogdetailpage_introduction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogdetailpage',
            name='introduction',
        ),
        migrations.AddField(
            model_name='blogdetailpage',
            name='description',
            field=wagtail.core.fields.RichTextField(blank=True, null=True),
        ),
    ]
