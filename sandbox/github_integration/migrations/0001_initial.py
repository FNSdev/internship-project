# Generated by Django 2.2.2 on 2019-06-19 11:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('url', models.URLField()),
                ('commit_sha', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('name', models.CharField(max_length=150)),
                ('url', models.URLField()),
                ('status', models.IntegerField(choices=[(0, 'updated'), (1, 'update_in_progress'), (2, 'deleted_on_github')], default=0)),
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repositories', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(0, 'file'), (1, 'dir')])),
                ('name', models.CharField(max_length=150)),
                ('url', models.URLField()),
                ('branch', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content', to='github_integration.Branch')),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content', to='github_integration.Content')),
            ],
        ),
        migrations.AddField(
            model_name='branch',
            name='repository',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='branches', to='github_integration.Repository'),
        ),
    ]
