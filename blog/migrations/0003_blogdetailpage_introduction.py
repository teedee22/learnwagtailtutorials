# Generated by Django 2.2.4 on 2019-08-29 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_blogauthor'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogdetailpage',
            name='introduction',
            field=models.CharField(blank=True, help_text='Write a small description of your post', max_length=300, null=True),
        ),
    ]
