# Generated by Django 2.2.2 on 2019-06-30 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20190630_1101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=150, unique=True),
        ),
    ]
