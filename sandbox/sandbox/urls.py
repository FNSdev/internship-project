import core.urls
import user.urls
import github_integration.urls
import api.urls
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include(user.urls, namespace='user')),
    path('github-integration/', include(github_integration.urls, namespace='github_integration')),
    path('api/v1/', include(api.urls, namespace='rest')),
    path('', include(core.urls, namespace='core')),
]
