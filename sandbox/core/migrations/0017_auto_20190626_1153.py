# Generated by Django 2.2.2 on 2019-06-26 11:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_activity_activity_type_alter_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'ordering': ['-date_time', 'activity_type']},
        ),
    ]