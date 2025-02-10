from django.urls import include, path
from rest_framework.routers import DefaultRouter
from djoser import views as djoser_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import (
    # AvatarUpdateViewSet,
    CustomUserViewSet,
    IngredientViewSet,
    RecipesViewSet,
    # SubscriptionViewSet,
    TagsViewSet
)

router = DefaultRouter()
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagsViewSet, basename='tags')
router.register('users', CustomUserViewSet, basename='users')
# router.register(r'users', djoser_views.UserViewSet, basename='user')
# router.register('avatar', AvatarUpdateViewSet, basename='avatar')
# router.register('subscriptions', SubscriptionViewSet, basename='subscription')


urls_ver1 = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path('v1/', include(urls_ver1)),

]
# urlpatterns = [
#     path('', include(router.urls)),
#     # path(r'auth/', include('djoser.urls.authtoken')),
#     path('auth/', include(router.urls)),  # Регистрация и управление пользователями
#     path('auth/token/login/', TokenObtainPairView.as_view(),
#          name='token_obtain_pair'),  # Получение токена
#     path('auth/token/refresh/', TokenRefreshView.as_view(),
#          name='token_refresh'),  # Обновление токена
# ]
