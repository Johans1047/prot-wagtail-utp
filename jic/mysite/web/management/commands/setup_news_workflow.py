from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from wagtail.models import (
    GroupApprovalTask,
    GroupPagePermission,
    Page,
    Workflow,
    WorkflowPage,
    WorkflowTask,
)

from web.models import BlogIndexPage, BlogPage


class Command(BaseCommand):
    help = "Configura noticias con grupos internos/externos y flujo de aprobacion"

    def handle(self, *args, **options):
        externos_group, _ = Group.objects.get_or_create(name="Noticias Externos")
        internos_group, _ = Group.objects.get_or_create(name="Noticias Internos")
        editores_group, _ = Group.objects.get_or_create(name="Noticias Editores")

        blog_ct = ContentType.objects.get_for_model(BlogPage)

        def assign_model_permissions(group, codenames):
            perms = Permission.objects.filter(content_type=blog_ct, codename__in=codenames)
            group.permissions.add(*perms)

        assign_model_permissions(externos_group, ["add_blogpage", "change_blogpage"])
        assign_model_permissions(internos_group, ["add_blogpage", "change_blogpage"])
        assign_model_permissions(editores_group, ["add_blogpage", "change_blogpage", "publish_blogpage"])

        news_index = BlogIndexPage.objects.first()
        if not news_index:
            root = Page.get_first_root_node()
            news_index = root.add_child(
                instance=BlogIndexPage(
                    title="Noticias",
                    slug="noticias",
                    intro="Actualizaciones de la JIC.",
                )
            )
            news_index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Pagina indice de noticias creada en /noticias/"))

        def assign_page_permissions(group, permission_types):
            page_ct = ContentType.objects.get_for_model(Page)
            codename_map = {
                "add": "add_page",
                "edit": "change_page",
                "publish": "publish_page",
                "lock": "lock_page",
                "unlock": "unlock_page",
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

        assign_page_permissions(externos_group, ["add", "edit"])
        assign_page_permissions(internos_group, ["add", "edit"])
        assign_page_permissions(editores_group, ["add", "edit", "publish", "lock", "unlock"])

        approval_task, _ = GroupApprovalTask.objects.get_or_create(
            name="Aprobacion de noticias",
            defaults={"active": True},
        )
        if not approval_task.active:
            approval_task.active = True
            approval_task.save(update_fields=["active"])

        approval_task.groups.set([editores_group])

        workflow, _ = Workflow.objects.get_or_create(name="Workflow Noticias", defaults={"active": True})
        if not workflow.active:
            workflow.active = True
            workflow.save(update_fields=["active"])

        WorkflowTask.objects.get_or_create(workflow=workflow, task=approval_task, defaults={"sort_order": 1})
        WorkflowPage.objects.get_or_create(page=news_index, workflow=workflow)

        self.stdout.write(self.style.SUCCESS("Workflow de noticias configurado."))
        self.stdout.write(
            self.style.WARNING(
                "Asigna usuarios a: Noticias Externos, Noticias Internos o Noticias Editores desde Wagtail Users."
            )
        )
