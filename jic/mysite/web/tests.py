from datetime import timedelta

from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import TestCase
from django.utils import timezone
from wagtail.images import get_image_model
from wagtail.models import Collection, GroupCollectionPermission, GroupPagePermission, Page
from django.contrib.auth.models import Permission

from .models import BlogIndexPage, BlogPage, CustomImage, Gallery, GalleryImage, site_content_settings


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


class SetupNewsWorkflowCommandTests(TestCase):
    def test_command_creates_news_image_collection_under_fotos(self):
        call_command("setup_news_workflow")

        root_collection = Collection.get_first_root_node()
        photos_collection = root_collection.get_children().filter(name="Fotos").first()

        self.assertIsNotNone(photos_collection)
        self.assertTrue(photos_collection.get_children().filter(name="Noticias").exists())

    def test_command_assigns_only_news_collection_permissions_for_customimage(self):
        call_command("setup_news_workflow")

        news_group = Group.objects.get(name="Noticias")
        image_ct = ContentType.objects.get(app_label="web", model="customimage")
        required_codenames = {"add_customimage", "change_customimage"}
        allowed_optional_codenames = {"choose_customimage"}

        collection_permissions = GroupCollectionPermission.objects.filter(
            group=news_group,
            permission__content_type=image_ct,
        )
        permission_codenames = set(
            collection_permissions.values_list("permission__codename", flat=True)
        )

        self.assertTrue(required_codenames.issubset(permission_codenames))
        self.assertTrue(
            permission_codenames.issubset(required_codenames.union(allowed_optional_codenames))
        )
        self.assertEqual(collection_permissions.values("collection_id").distinct().count(), 1)

        noticias_collection = Collection.objects.get(name="Noticias", depth=3)
        noticias_permissions = Permission.objects.filter(
            content_type=image_ct,
            codename__in=required_codenames.union(allowed_optional_codenames),
        )
        for permission in noticias_permissions:
            self.assertTrue(
                GroupCollectionPermission.objects.filter(
                    group=news_group,
                    collection=noticias_collection,
                    permission=permission,
                ).exists()
            )

    def test_command_grants_publish_page_permission_on_news_index(self):
        call_command("setup_news_workflow")

        news_group = Group.objects.get(name="Noticias")
        news_index = BlogIndexPage.objects.first()
        page_ct = ContentType.objects.get_for_model(Page)
        publish_permission = Permission.objects.get(content_type=page_ct, codename="publish_page")

        self.assertTrue(
            GroupPagePermission.objects.filter(
                group=news_group,
                page=news_index,
                permission=publish_permission,
            ).exists()
        )


class SiteContentSettingsTests(TestCase):
    def test_singleton_defaults_are_available(self):
        settings_obj = site_content_settings.get_singleton()

        self.assertEqual(settings_obj.pk, 1)
        self.assertEqual(settings_obj.platform_url, "https://jic.utp.ac.pa")
        self.assertTrue(settings_obj.quick_section_title)
        self.assertTrue(settings_obj.faq_section_title)


class NewsImageCollectionSyncTests(TestCase):
    @staticmethod
    def _tiny_png_bytes() -> bytes:
        return (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?"
            b"\x00\x05\xfe\x02\xfeA\x89\xb7\x9b\x00\x00\x00\x00IEND\xaeB`\x82"
        )

    def _create_news_page_with_image(self, slug: str, title: str, image: CustomImage) -> BlogPage:
        root_page = Page.get_first_root_node()
        blog_index = root_page.get_children().type(BlogIndexPage).specific().first()
        if not blog_index:
            blog_index = BlogIndexPage(title="Noticias", slug="noticias")
            root_page.add_child(instance=blog_index)
            blog_index.save_revision().publish()

        news_page = BlogPage(
            title=title,
            slug=slug,
            excerpt="Prueba",
            cover_image=image,
            body=[("image", image)],
        )
        blog_index.add_child(instance=news_page)
        news_page.save_revision().publish()
        return news_page

    def test_news_images_are_moved_to_fotos_noticias_collection(self):
        root_collection = Collection.get_first_root_node()
        temp_collection = root_collection.add_child(instance=Collection(name="Temporal Noticias Test"))

        image = CustomImage(title="Imagen usada en noticia", collection=temp_collection)
        image.file.save("noticia-sync.png", ContentFile(self._tiny_png_bytes()), save=True)

        self._create_news_page_with_image(
            slug="noticia-con-imagen",
            title="Noticia con imagen",
            image=image,
        )

        image.refresh_from_db()
        self.assertEqual(image.collection.name, "Noticias")
        self.assertIsNotNone(image.collection.get_parent())
        self.assertEqual(image.collection.get_parent().name, "Fotos")

    def test_news_image_is_removed_from_noticias_when_no_longer_referenced(self):
        root_collection = Collection.get_first_root_node()
        temp_collection = root_collection.add_child(instance=Collection(name="Temporal Noticias Remove Test"))

        image = CustomImage(title="Imagen removida de noticia", collection=temp_collection)
        image.file.save("noticia-remove-sync.png", ContentFile(self._tiny_png_bytes()), save=True)

        news_page = self._create_news_page_with_image(
            slug="noticia-remove-imagen",
            title="Noticia remove imagen",
            image=image,
        )

        image.refresh_from_db()
        self.assertEqual(image.collection.name, "Noticias")

        news_page.cover_image = None
        news_page.body = []
        news_page.save_revision().publish()

        image.refresh_from_db()
        self.assertEqual(image.collection.name, "Fotos")

    def test_news_image_stays_in_noticias_if_still_used_by_another_news(self):
        root_collection = Collection.get_first_root_node()
        temp_collection = root_collection.add_child(instance=Collection(name="Temporal Noticias Shared Test"))

        shared_image = CustomImage(title="Imagen compartida", collection=temp_collection)
        shared_image.file.save("noticia-shared-sync.png", ContentFile(self._tiny_png_bytes()), save=True)

        first_news_page = self._create_news_page_with_image(
            slug="noticia-shared-1",
            title="Noticia shared 1",
            image=shared_image,
        )
        self._create_news_page_with_image(
            slug="noticia-shared-2",
            title="Noticia shared 2",
            image=shared_image,
        )

        first_news_page.cover_image = None
        first_news_page.body = []
        first_news_page.save_revision().publish()

        shared_image.refresh_from_db()
        self.assertEqual(shared_image.collection.name, "Noticias")


class GalleryAdminDataEndpointTests(TestCase):
    @staticmethod
    def _tiny_png_bytes() -> bytes:
        return (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?"
            b"\x00\x05\xfe\x02\xfeA\x89\xb7\x9b\x00\x00\x00\x00IEND\xaeB`\x82"
        )

    def setUp(self):
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_user(
            username="gallery_admin",
            email="gallery_admin@example.com",
            password="gallery_admin_password_123",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(self.admin_user)

        root_collection = Collection.get_first_root_node()
        self.collection = root_collection.add_child(instance=Collection(name="Gallery Endpoint Test"))
        self.gallery = Gallery.objects.create(title="Galería Test")

        image_model = get_image_model()
        now = timezone.now()

        def make_image(name: str, created_at_offset_days: int):
            image = image_model(title=name, collection=self.collection)
            image.file.save(f"{name}.png", ContentFile(self._tiny_png_bytes()), save=True)
            image_model.objects.filter(pk=image.pk).update(created_at=now - timedelta(days=created_at_offset_days))
            image.refresh_from_db()
            return image

        image_2026_old = make_image("img-2026-old", 30)
        image_2026_new = make_image("img-2026-new", 5)
        image_2024 = make_image("img-2024", 12)
        image_none_old = make_image("img-none-old", 60)
        image_none_new = make_image("img-none-new", 10)

        self.item_2026_old = GalleryImage.objects.create(gallery=self.gallery, image=image_2026_old, year=2026)
        self.item_2026_new = GalleryImage.objects.create(gallery=self.gallery, image=image_2026_new, year=2026)
        self.item_2024 = GalleryImage.objects.create(gallery=self.gallery, image=image_2024, year=2024)
        self.item_none_old = GalleryImage.objects.create(gallery=self.gallery, image=image_none_old, year=None)
        self.item_none_new = GalleryImage.objects.create(gallery=self.gallery, image=image_none_new, year=None)

    def test_endpoint_returns_consistent_order_for_all(self):
        response = self.client.get(f"/panel/admin/snippets/web/gallery/images-data/{self.gallery.pk}/?year=all")
        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertEqual(payload["available_years"], [2026, 2024])
        self.assertEqual(
            payload["ordered_ids"],
            [
                self.item_2026_new.pk,
                self.item_2026_old.pk,
                self.item_2024.pk,
                self.item_none_new.pk,
                self.item_none_old.pk,
            ],
        )

        group_keys = [group["key"] for group in payload["groups"]]
        self.assertEqual(group_keys, ["2026", "2024", "unclassified"])

    def test_endpoint_filters_by_year(self):
        response = self.client.get(f"/panel/admin/snippets/web/gallery/images-data/{self.gallery.pk}/?year=2026")
        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertEqual(payload["ordered_ids"], [self.item_2026_new.pk, self.item_2026_old.pk])
        self.assertEqual([group["key"] for group in payload["groups"]], ["2026"])

    def test_endpoint_filters_unclassified(self):
        response = self.client.get(
            f"/panel/admin/snippets/web/gallery/images-data/{self.gallery.pk}/?year=unclassified"
        )
        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertEqual(payload["ordered_ids"], [self.item_none_new.pk, self.item_none_old.pk])
        self.assertEqual([group["key"] for group in payload["groups"]], ["unclassified"])
