# Generated by Django 2.2.2 on 2019-06-17 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('github_integration', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='status',
            field=models.IntegerField(choices=[(0, 'updated'), (1, 'update_in_progress')], default=0),
        ),
    ]