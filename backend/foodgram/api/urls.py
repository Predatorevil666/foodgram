from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    AvatarUpdateViewSet,
    CustomUserViewSet,
    IngredientViewSet,
    RecipesViewSet,
    SubscriptionViewSet,
    TagsViewSet
)

router_v1 = DefaultRouter()
router_v1.register('recipes', RecipesViewSet, basename='recipes')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('tags', TagsViewSet, basename='tags')
router_v1.register('users', CustomUserViewSet, basename='users')
router_v1.register('avatar', AvatarUpdateViewSet, basename='avatar')
router_v1.register(
    'subscriptions',
    SubscriptionViewSet,
    basename='subscription'
)


urls_ver1 = [
    path('', include(router_v1.urls)),
]

urlpatterns = [
    path('v1/', include(urls_ver1)),

]
