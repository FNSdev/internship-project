from api.views import ProjectViewSet, UserViewSet, TaskViewSet
from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'users', UserViewSet)
router.register(r'users/(?P<owner_email>[^/]+)/projects', ProjectViewSet)
router.register(r'users/(?P<owner_email>[^/]+)/projects/(?P<project_name>[^/]+)/tasks', TaskViewSet)

app_name = 'api'
urlpatterns = router.urls
