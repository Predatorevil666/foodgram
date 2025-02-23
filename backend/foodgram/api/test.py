def test_anonymous_user_access(self):
    """Тест для неавторизованного пользователя."""
    response = self.client.get('/api/recipes/')
    self.assertEqual(response.status_code, 200)

    response = self.client.post('/api/recipes/1/favorite/')
    self.assertEqual(response.status_code, 401)
