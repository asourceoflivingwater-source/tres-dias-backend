"""
Создаёт департаменты по списку «Порядок представления департаментов».

Идемпотентно: уже существующие slug не перезаписываются.
Запуск: python management_portal/manage.py create_departments
"""

from django.core.management.base import BaseCommand
from slugify import slugify

from apps.department.models import Department

# Порядок как в регламенте (названия — как в документе).
DEPARTMENT_TITLES = [
    "Восхваление",
    "Молитва",
    "Роерум",
    "Кухня",
    "Паланка",
    "Рефрешмент",
    "Декорация",
    "Столовая",
    "Сетап",
    "Звонарь",
    "Фото",
    "Администрация",
    "Ректорат",
    "Духовенство",
]


class Command(BaseCommand):
    help = "Создаёт фиксированный набор департаментов (по порядку представления)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--update-titles",
            action="store_true",
            help="Если департамент с таким slug уже есть — обновить title из списка.",
        )

    def handle(self, *args, **options):
        update_titles = options["update_titles"]
        created = 0
        skipped = 0
        updated = 0

        for title in DEPARTMENT_TITLES:
            slug = slugify(title)
            obj, was_created = Department.objects.get_or_create(
                slug=slug,
                defaults={"title": title, "description": ""},
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"+ создан: {title} (slug={slug})"))
            else:
                if update_titles and obj.title != title:
                    obj.title = title
                    obj.save(update_fields=["title", "updated_at"])
                    updated += 1
                    self.stdout.write(self.style.WARNING(f"~ обновлён title: {slug} → {title}"))
                else:
                    skipped += 1
                    self.stdout.write(f"= уже есть: {obj.title} (slug={slug})")

        self.stdout.write(
            self.style.SUCCESS(
                f"Итого: создано {created}, без изменений {skipped}, обновлено title {updated}."
            )
        )
