from django.urls import include, path
from rest_framework.routers import DefaultRouter


from api.views import (
    # AvatarUpdateViewSet,
    CustomUserViewSet,
    IngredientViewSet,
    RecipesViewSet,
    SubscriptionViewSet,
    TagsViewSet
)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(r'recipes', RecipesViewSet, basename='recipes')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagsViewSet, basename='tags')
router_v1.register(r'users', CustomUserViewSet, basename='users')

urls_ver1 = [
    path(
        'users/subscriptions/',
        SubscriptionViewSet.as_view(
            {'get': 'list'}),
        name='subscriptions'
    ),
    path(
        'users/<int:pk>/subscribe/',
        SubscriptionViewSet.as_view(
            {'post': 'subscribe', 'delete': 'subscribe'}),
        name='subscribe'
    ),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path('v1/', include(urls_ver1)),

]
