from django.db import migrations, models


def int_to_str_activity_type(apps, schema_editor):
    Activity = apps.get_model('core', 'Activity')
    for activity in Activity.objects.all():
        if activity.temp_activity_type == 0:
            activity.activity_type = 'TASK_WAS_CREATED'
        elif activity.temp_activity_type == 1:
            activity.activity_type = 'TASK_WAS_UPDATED'
        elif activity.temp_activity_type == 2:
            activity.activity_type = 'TASK_WAS_COMPLETED'
        elif activity.temp_activity_type == 3:
            activity.activity_type = 'BRANCH_WAS_UPDATED'
        else:
            activity.activity_type = 'UNKNOWN_ACTIVITY'
        activity.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_activity_project'),
    ]

    operations = [
        migrations.RenameField(
            model_name='activity',
            old_name='activity_type',
            new_name='temp_activity_type',
        ),
        migrations.AddField(
            model_name='activity',
            name='activity_type',
            field=models.CharField(
                choices=[
                    ('TASK_WAS_CREATED', 'task was created'),
                    ('TASK_WAS_UPDATED', 'task was updated'),
                    ('TASK_WAS_COMPLETED', 'task was completed'),
                    ('BRANCH_WAS_UPDATED', 'branch was updated'),
                    ('UNKNOWN_ACTIVITY', 'unknown activity'),
                ],
                max_length=50,
                default='UNKNOWN_ACTIVITY',
            )
        ),
        migrations.RunPython(int_to_str_activity_type),
        migrations.RemoveField(
            model_name='Activity',
            name='temp_activity_type'
        ),
    ]
