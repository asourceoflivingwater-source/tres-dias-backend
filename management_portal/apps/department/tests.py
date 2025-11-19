from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from apps.users.models import User
from apps.department.models import Department, DepartmentMember
from .models import DepartmentRole
from apps.sections.models import DepartmentSection

class DepartmentMemberTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345', email='admin@mail.ru' ,is_staff=True)
        self.client.force_authenticate(user=self.user)
        self.test_member = User.objects.create_user(username='testmember', password='12345', email='test@mail.ru')
        self.department = Department.objects.create(title='HR', slug='hr')

    def test_add_member(self):
        url = reverse('department-members-view', kwargs={'department_id': self.department.id})
        data = {
            'user_email': self.test_member.email,
            'role': DepartmentRole.VIEWER
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['role'], data['role'])
    
class DepartmentSectionsTest(APITestCase):
    def setUp(self):
        self.department = Department.objects.create(title='HR', slug='hr')
        sections = [
        DepartmentSection(department=self.department, type='HOME', title='public section', visibility='public', status='published'),
        DepartmentSection(department=self.department, type='TEAM-INFO', title='member section', visibility='members', status='published'),
        DepartmentSection(department=self.department, type='CHIEF-INFO', title='assistant section', visibility='role_based', status='published', visible_for_roles=['chief', 'assistant'])
        ]
        DepartmentSection.objects.bulk_create(sections)

    def test_get_sections(self):
        url = reverse('department_sections_view', kwargs={'slug': self.department.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'public section')

class AuthenticatedSectionsTest(DepartmentSectionsTest):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='testuser', password='12345', email='admin@mail.ru' ,is_staff=True)
        self.client.force_authenticate(user=self.user)
    
    def test_get_sections(self):
        url = reverse('department_sections_view', kwargs={'slug': self.department.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

class RoleScopedSectionsTest(DepartmentSectionsTest):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='testuser', password='12345', email='test@mail.ru' ,is_staff=False)
        self.department_member = DepartmentMember.objects.create(role='assistant', user=self.user, department=self.department)
        self.client.force_authenticate(user=self.user)
        
    def test_get_sections(self):
        url = reverse('department_sections_view', kwargs={'slug': self.department.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], 'public section')
        self.assertEqual(response.data[1]['title'], 'assistant section')