import factory
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    # Use a sequence so you don't get 'Duplicate Username' errors
    username = factory.Sequence(lambda n: 'user_%d' % n)
    email = factory.LazyAttribute(lambda o: '%s@mail.ru' % o.username)
    is_superuser = False
    # This handles password hashing correctly
    password = factory.PostGenerationMethodCall('set_password', '12345')