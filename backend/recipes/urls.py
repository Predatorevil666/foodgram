from django.urls import path

from recipes.views import recipe_redirect

app_name = 'recipes'

urlpatterns = [
    path('<slug:slug>/', recipe_redirect, name='short-link-redirect'),
]
