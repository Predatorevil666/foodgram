from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from recipes.models import Recipe


def recipe_redirect(request, slug):
    """Простой редирект без бесконечных циклов"""
    recipe = get_object_or_404(Recipe, slug=slug)
    return HttpResponseRedirect(f'/recipes/{recipe.id}/')
