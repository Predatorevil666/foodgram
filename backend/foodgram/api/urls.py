from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import RecipeViewSet, IngredientViewSet, TagViewSet


router_v1 = DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('tags', TagViewSet, basename='tags')


urls_ver1 = [
    path('', include(router_v1.urls)),
]

urlpatterns = [
    path('v1/', include(urls_ver1)),

]
