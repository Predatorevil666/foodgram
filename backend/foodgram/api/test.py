def test_anonymous_user_access(self):
    """Тест для неавторизованного пользователя."""
    response = self.client.get('/api/recipes/')
    self.assertEqual(response.status_code, 200)
    
    response = self.client.post('/api/recipes/1/favorite/')
    self.assertEqual(response.status_code, 401)  # Должна быть ошибка

# def test_shopping_list_sum(self):
#     """Тест для списка покупок."""
#     user = UserFactory()
#     ingredient = IngredientFactory(name='Сахар')
#     recipe1 = RecipeFactory()
#     recipe2 = RecipeFactory()
    
#     # Добавляем ингредиент в два рецепта
#     IngredientInRecipe.objects.create(recipe=recipe1, ingredient=ingredient, quantity=100)
#     IngredientInRecipe.objects.create(recipe=recipe2, ingredient=ingredient, quantity=200)
    
#     # Добавляем рецепты в корзину
#     ShoppingCart.objects.create(user=user, recipe=recipe1)
#     ShoppingCart.objects.create(user=user, recipe=recipe2)
    
#     response = self.client.get('/api/recipes/download_shopping_cart/')
#     self.assertIn('Сахар (г) — 300', response.content.decode())