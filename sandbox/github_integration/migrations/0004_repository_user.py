# Generated by Django 2.2.2 on 2019-06-17 10:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('github_integration', '0003_auto_20190617_0930'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
