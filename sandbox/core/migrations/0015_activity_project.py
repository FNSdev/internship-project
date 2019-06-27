# Generated by Django 2.2.2 on 2019-06-25 11:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_activity_date_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='core.Project'),
        ),
    ]
