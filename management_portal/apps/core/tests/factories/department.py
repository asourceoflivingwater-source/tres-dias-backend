import factory
from slugify import slugify
from .user import UserFactory
from apps.department.models import Department, DepartmentMember


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department
        django_get_or_create = ("title",)

    title = factory.Sequence(lambda n: "Department %d" % n)
    slug = factory.LazyAttribute(lambda o: slugify(o.title))
    description = factory.LazyAttribute(
        lambda o: "Desription for depeartment - %s with slug %s" % (o.title, o.slug)
    )
    chief = factory.SubFactory(UserFactory)


class DepartmentMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DepartmentMember

    user = factory.SubFactory(UserFactory)
    department = factory.SubFactory(DepartmentFactory)
    role = "viewer"
