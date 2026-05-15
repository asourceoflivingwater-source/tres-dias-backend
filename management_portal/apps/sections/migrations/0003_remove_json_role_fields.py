# sections/migrations/0003_remove_json_role_fields.py
#
# ШАГ 2 из 2:
#   1. Перенести данные из JSON-полей секции в SectionPermission (backfill)
#   2. Инициализировать SectionPermission для секций у которых записей нет
#   3. Удалить три JSON-поля с sections_departmentsection
#
# Зависит от 0002 (UniqueConstraint уже есть)

from django.db import migrations

# ── Все роли из нашего enum ──────────────────────────────────────────────
ALL_ROLES = ["admin", "chief", "assistant", "secretary", "team_member", "viewer"]

# ── Дефолтные права при инициализации ───────────────────────────────────
DEFAULTS = {
    "admin":       {"can_view": True,  "can_edit": True,  "can_publish": True},
    "chief":       {"can_view": True,  "can_edit": True,  "can_publish": True},
    "assistant":   {"can_view": True,  "can_edit": False, "can_publish": False},
    "secretary":   {"can_view": True,  "can_edit": False, "can_publish": False},
    "team_member": {"can_view": True,  "can_edit": False, "can_publish": False},
    "viewer":      {"can_view": True,  "can_edit": False, "can_publish": False},
}


def backfill_section_permissions(apps, schema_editor):
    SectionPermission = apps.get_model("sections", "SectionPermission")
    DepartmentSection = apps.get_model("sections", "DepartmentSection")

    import uuid as uuid_mod

    for section in DepartmentSection.objects.all():
        visible_roles  = section.visible_for_roles  or []
        edit_roles     = section.allow_edit_roles    or []
        publish_roles  = section.allow_publish_roles or []

        for role in ALL_ROLES:
            defaults = dict(DEFAULTS[role])

            if visible_roles:
                defaults["can_view"] = role in visible_roles
            if edit_roles and role in edit_roles:
                defaults["can_edit"] = True
            if publish_roles and role in publish_roles:
                defaults["can_publish"] = True

            obj, created = SectionPermission.objects.get_or_create(
                section_id=section.pk,
                role=role,
                defaults={
                    "id": uuid_mod.uuid4(),
                    "can_view":    defaults["can_view"],
                    "can_edit":    defaults["can_edit"],
                    "can_publish": defaults["can_publish"],
                },
            )
            if not created:
                changed = False
                if visible_roles and obj.can_view != defaults["can_view"]:
                    obj.can_view = defaults["can_view"]
                    changed = True
                if edit_roles and obj.can_edit != defaults["can_edit"]:
                    obj.can_edit = defaults["can_edit"]
                    changed = True
                if publish_roles and obj.can_publish != defaults["can_publish"]:
                    obj.can_publish = defaults["can_publish"]
                    changed = True
                if changed:
                    obj.save(update_fields=["can_view", "can_edit", "can_publish"])


def reverse_backfill(apps, schema_editor):
    SectionPermission = apps.get_model("sections", "SectionPermission")
    DepartmentSection = apps.get_model("sections", "DepartmentSection")

    for section in DepartmentSection.objects.all():
        perms = {
            p.role: p
            for p in SectionPermission.objects.filter(section_id=section.pk)
        }
        section.visible_for_roles  = [r for r, p in perms.items() if p.can_view]
        section.allow_edit_roles   = [r for r, p in perms.items() if p.can_edit]
        section.allow_publish_roles = [r for r, p in perms.items() if p.can_publish]
        section.save(update_fields=[
            "visible_for_roles", "allow_edit_roles", "allow_publish_roles"
        ])


class Migration(migrations.Migration):

    dependencies = [
        ("sections", "0002_sectionpermission_unique_and_role_enum"),
    ]

    operations = [
        # ── 1. Backfill SectionPermission из JSON-полей ───────────────────
        migrations.RunPython(
            backfill_section_permissions,
            reverse_backfill,
        ),

        # ── 2. Удалить три JSON-поля ──────────────────────────────────────
        migrations.RemoveField(
            model_name="departmentsection",
            name="visible_for_roles",
        ),
        migrations.RemoveField(
            model_name="departmentsection",
            name="allow_edit_roles",
        ),
        migrations.RemoveField(
            model_name="departmentsection",
            name="allow_publish_roles",
        ),
    ]
