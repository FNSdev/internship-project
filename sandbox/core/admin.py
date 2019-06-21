from django.contrib import admin
from core.models import Project, Task, Invite


admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Invite)
