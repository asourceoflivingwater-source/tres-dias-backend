import factory
from factory import fuzzy
from factory.django import DjangoModelFactory, FileField
from .user import UserFactory
from apps.adminapp.models import Comment, CommentAttachment
from .department import DepartmentFactory


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    department = factory.SubFactory(DepartmentFactory)
    author = factory.SubFactory(UserFactory)

    author_role = "chief"

    label = factory.Sequence(lambda n: f"Label {n}")
    body = factory.Faker("paragraph", nb_sentences=3)

    tags = factory.List([factory.Faker("word"), factory.Faker("word")])

    meta = factory.Dict(
        {
            "browser": "Chrome",
            "ip_address": factory.Faker("ipv4"),
            "priority": fuzzy.FuzzyInteger(1, 5),
        }
    )

    is_admin_only = True


class CommentAttachmentFactory(DjangoModelFactory):
    class Meta:
        model = CommentAttachment

    comment = factory.SubFactory(CommentFactory)
    file = FileField(filename="document.pdf", data=b"fake pdf content")
    filename = factory.LazyAttribute(lambda obj: obj.file.name)
    meta = factory.Dict({"size": 1024, "content_type": "application/pdf"})


7
