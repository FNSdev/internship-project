# Generated by Django 2.2.2 on 2019-06-17 10:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('github_integration', '0004_repository_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
