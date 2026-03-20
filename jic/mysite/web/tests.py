from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.models import Page

from .models import BlogIndexPage, BlogPage


class CriticalRoutesTests(TestCase):
    def test_public_critical_pages_are_available(self):
        client = self.client

        self.assertEqual(client.get("/").status_code, 200)
        self.assertEqual(client.get("/busqueda/").status_code, 200)
        self.assertEqual(client.get("/noticias/").status_code, 200)

    def test_invalid_documents_subpath_returns_404(self):
        response = self.client.get("/panel/documents/no-existe/")
        self.assertEqual(response.status_code, 404)

    def test_invalid_admin_subpath_redirects_for_anonymous_user(self):
        response = self.client.get("/panel/admin/no-existe/")
        self.assertEqual(response.status_code, 302)

    def test_invalid_admin_subpath_returns_404_for_authenticated_admin(self):
        user_model = get_user_model()
        admin_user = user_model.objects.create_user(
            username="admin_test",
            email="admin_test@example.com",
            password="admin_test_password_123",
            is_staff=True,
            is_superuser=True,
        )

        self.client.force_login(admin_user)
        response = self.client.get("/panel/admin/no-existe/")
        self.assertEqual(response.status_code, 404)


class NewsRoutesTests(TestCase):
    def test_news_detail_returns_200_for_live_public_post(self):
        root = Page.get_first_root_node()

        index = BlogIndexPage(title="Noticias", slug="noticias")
        root.add_child(instance=index)
        index.save_revision().publish()

        post = BlogPage(
            title="Noticia de prueba",
            slug="noticia-prueba",
            excerpt="Resumen de prueba",
        )
        index.add_child(instance=post)
        post.save_revision().publish()

        response = self.client.get("/noticias/noticia-prueba/")
        self.assertEqual(response.status_code, 200)
