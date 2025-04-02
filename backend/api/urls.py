from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, RecipeRedirectView, RecipesViewSet,
                       SubscriptionViewSet, TagsViewSet, UserViewSet)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('recipes', RecipesViewSet, basename='recipes')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('tags', TagsViewSet, basename='tags')
router_v1.register('users', UserViewSet, basename='users')

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
            {'post': 'subscribe', 'delete': 'unsubscribe'}),
        name='subscribe'
    ),

    path(
        'r/<slug:slug>/',
        RecipeRedirectView.as_view(),
        name='recipe-redirect'
    ),

    path('auth/', include('djoser.urls.authtoken')),

    path('', include(router_v1.urls)),
]

urlpatterns = [
    path('v1/', include(urls_ver1)),
]
