import factory
from .department import DepartmentFactory
from apps.sections.models import (
    DepartmentSection,
    SectionType,
    SectionStatus,
    VisibilityType,
)


class SectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DepartmentSection
        django_get_or_create = (
            "department",
            "type",
        )

    department = factory.SubFactory(DepartmentFactory)
    title = factory.Sequence(lambda n: "Section %d" % n)
    type = SectionType.HOME
    status = SectionStatus.PUBLISHED
    visibility = VisibilityType.PUBLIC
