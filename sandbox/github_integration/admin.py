from django.contrib import admin
from github_integration.models import Repository, Branch, Content


admin.site.register(Repository)
admin.site.register(Branch)
admin.site.register(Content)
