from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from apps.users.models import User
from apps.department.models import Department

class DepartmentListTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345', is_staff=True)
        self.client.force_authenticate(user=self.user)
        departments_to_create = [
            Department(title='HR', slug='hr', chief=self.user),
            Department(title='Engineering', slug='eng', chief=self.user),
            Department(title='Sales', slug='sales', chief=self.user),
            Department(title='Marketing', slug='mark', chief=self.user),
        ]

        Department.objects.bulk_create(departments_to_create)
        self.departments = Department.objects.all()

    def test_list_departments(self):
        
        url = reverse('departments_view') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(Department.objects.count(), 0)

    def test_create_department(self):
        url = reverse('departments_view') 
        data = {
            'title': 'Test Department',
            'slug': 'test-department-1',
            'description': 'department description',
            'chief': self.user.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Department')
    
    def test_retrieve_department(self): 
        url = reverse('department_profile_view', kwargs={'slug': self.departments[0].slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.departments[0].title)

    def test_update_department(self):
        url = reverse('department_profile_view', kwargs={'slug': self.departments[0].slug})
        data = {
            'title': 'Updated title',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.data['title'], 'Updated title')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_department(self):
        url = reverse('department_profile_view', kwargs={'slug': self.departments[0].slug})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
   