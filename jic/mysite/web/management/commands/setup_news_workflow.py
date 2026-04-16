from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from wagtail.models import (
    Collection,
    GroupCollectionPermission,
    GroupPagePermission,
    Page,
    Site,
    WorkflowPage,
)

from web.models import BlogIndexPage, BlogPage


class Command(BaseCommand):
    help = "Configura noticias con un unico rol que solo puede subir noticias"

    @staticmethod
    def _get_or_create_child_collection(parent, name):
        """Return a direct child collection with the given name, creating it when missing."""
        collection = parent.get_children().filter(name=name).first()
        if collection:
            return collection
        return parent.add_child(instance=Collection(name=name))

    def _ensure_news_image_collection(self):
        """Ensure photo collections contain Fotos/Noticias and return Noticias collection."""
        root_collection = Collection.get_first_root_node()
        photos_collection = self._get_or_create_child_collection(root_collection, "Fotos")

        news_collection = Collection.objects.filter(name="Noticias").exclude(pk=photos_collection.pk).first()
        if news_collection and news_collection.get_parent() and news_collection.get_parent().id != photos_collection.id:
            news_collection.move(photos_collection, pos="last-child")

        if not news_collection or not news_collection.get_parent() or news_collection.get_parent().id != photos_collection.id:
            news_collection = self._get_or_create_child_collection(photos_collection, "Noticias")

        return news_collection

    @staticmethod
    def _assign_news_collection_permissions(news_group, news_collection):
        """Restrict image collection permissions for Noticias group to the Noticias collection only."""
        image_ct = ContentType.objects.get(app_label="web", model="customimage")

        image_collection_perms = Permission.objects.filter(
            content_type=image_ct,
            codename__in=["add_customimage", "change_customimage", "choose_customimage"],
        )

        GroupCollectionPermission.objects.filter(
            group=news_group,
            permission__content_type=image_ct,
        ).delete()

        for permission in image_collection_perms:
            GroupCollectionPermission.objects.get_or_create(
                group=news_group,
                collection=news_collection,
                permission=permission,
            )

    def handle(self, *args, **options):
        news_group, _ = Group.objects.get_or_create(name="Noticias")

        # Consolidate legacy news groups into the single Noticias role.
        legacy_group_names = ["Noticias Externos", "Noticias Internos", "Noticias Editores"]
        for legacy_name in legacy_group_names:
            legacy_group = Group.objects.filter(name=legacy_name).first()
            if not legacy_group:
                continue

            for user in legacy_group.user_set.all():
                user.groups.add(news_group)

            legacy_group.delete()

        blog_ct = ContentType.objects.get_for_model(BlogPage)

        # Keep only add/change permissions for BlogPage to allow uploading/editing news drafts.
        blog_perms = Permission.objects.filter(content_type=blog_ct)
        news_group.permissions.remove(*blog_perms)
        allowed_blog_perms = Permission.objects.filter(
            content_type=blog_ct,
            codename__in=["add_blogpage", "change_blogpage"],
        )
        news_group.permissions.add(*allowed_blog_perms)

        # Required by Wagtail for non-superusers to enter the admin UI.
        access_admin_perm = Permission.objects.filter(codename="access_admin").first()
        if access_admin_perm:
            news_group.permissions.add(access_admin_perm)

        default_site = Site.objects.filter(is_default_site=True).first()
        site_root = default_site.root_page if default_site else Page.get_first_root_node()

        news_index = BlogIndexPage.objects.first()
        if not news_index:
            news_index = site_root.add_child(
                instance=BlogIndexPage(
                    title="Noticias",
                    slug="noticias",
                    intro="Actualizaciones de la JIC.",
                )
            )
            news_index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Pagina indice de noticias creada en /noticias/"))
        elif not news_index.path.startswith(site_root.path):
            # Keep the news section inside the default Site tree to avoid admin warnings.
            news_index.move(site_root, pos="last-child")
            news_index.save_revision().publish()
            self.stdout.write(
                self.style.SUCCESS("Pagina indice de noticias movida bajo la raiz del sitio por defecto.")
            )

        # Ensure the page is published and shows as live in admin.
        if not news_index.live:
            news_index.save_revision().publish()
            self.stdout.write(
                self.style.SUCCESS("Pagina indice de noticias publicada.")
            )

        def assign_page_permissions(group, permission_types):
            page_ct = ContentType.objects.get_for_model(Page)
            codename_map = {
                "add": "add_page",
                "edit": "change_page",
                "publish": "publish_page",
            }

            for permission_type in permission_types:
                codename = codename_map.get(permission_type)
                if not codename:
                    continue

                permission = Permission.objects.get(content_type=page_ct, codename=codename)
                GroupPagePermission.objects.get_or_create(
                    group=group,
                    page=news_index,
                    permission=permission,
                )

        # Reset page-level permissions for this role and keep add/edit/publish on the news index.
        GroupPagePermission.objects.filter(group=news_group).delete()
        assign_page_permissions(news_group, ["add", "edit", "publish"])

        # Remove workflow assignment from news index so this role cannot indirectly publish.
        WorkflowPage.objects.filter(page=news_index).delete()

        # Ensure users assigned to Noticias can pass Django admin staff gate.
        for user in news_group.user_set.all():
            if not user.is_staff:
                user.is_staff = True
                user.save(update_fields=["is_staff"])

        news_image_collection = self._ensure_news_image_collection()
        self._assign_news_collection_permissions(news_group, news_image_collection)

        self.stdout.write(self.style.SUCCESS("Rol unico de noticias configurado: Noticias"))
        self.stdout.write(self.style.SUCCESS("Permisos aplicados: crear/editar/publicar noticias."))
        self.stdout.write(
            self.style.SUCCESS(
                "Coleccion de imagenes configurada: Fotos/Noticias (solo para el grupo Noticias)."
            )
        )
        self.stdout.write(self.style.WARNING("Asigna usuarios unicamente al grupo: Noticias."))
