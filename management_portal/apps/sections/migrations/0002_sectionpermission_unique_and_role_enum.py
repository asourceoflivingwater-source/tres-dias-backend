# sections/migrations/0002_sectionpermission_unique_and_role_enum.py
#
# ШАГ 1 из 2:
#   - Добавить UniqueConstraint(section, role) на SectionPermission
#   - Убрать дубли перед добавлением ограничения (безопасно)
#
# Применять ПЕРЕД 0003 (удаление JSON-полей)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sections", "0001_initial"),
    ]

    operations = [
        # ── 1. Удалить дубли (section_id, role) перед добавлением UNIQUE ──
        migrations.RunSQL(
            sql="""
            DELETE FROM sections_sectionpermission a
            USING sections_sectionpermission b
            WHERE a.id > b.id
              AND a.section_id = b.section_id
              AND a.role = b.role;
            """,
            reverse_sql=migrations.RunSQL.noop,
            hints={"target": "sections_sectionpermission"},
        ),

        # ── 2. Добавить UniqueConstraint(section, role) ─────────────────
        migrations.AddConstraint(
            model_name="sectionpermission",
            constraint=models.UniqueConstraint(
                fields=["section", "role"],
                name="unique_section_role_permission",
            ),
        ),
    ]
