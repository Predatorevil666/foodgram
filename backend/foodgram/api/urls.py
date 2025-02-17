from django.urls import include, path
from rest_framework.routers import DefaultRouter


from api.views import (
    # AvatarUpdateViewSet,
    CustomUserViewSet,
    IngredientViewSet,
    RecipesViewSet,
    TagsViewSet
)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(r'recipes', RecipesViewSet, basename='recipes')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagsViewSet, basename='tags')
router_v1.register(r'users', CustomUserViewSet, basename='users')
# router_v1.register(
#     r'users/me/avatar',
#     AvatarUpdateViewSet,
#     basename='user-avatar'


urls_ver1 = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path('v1/', include(urls_ver1)),

]
