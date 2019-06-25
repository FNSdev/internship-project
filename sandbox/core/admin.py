from django.contrib import admin
from core.models import Project, Task, Invite, Activity


admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Invite)
admin.site.register(Activity)
