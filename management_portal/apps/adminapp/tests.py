from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from apps.users.models import User
from apps.department.models import Department

from .models import Comment

class CommentModelTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345', is_staff=True)
        self.department = Department.objects.create(title='test_department', chief=self.user, slug='test-department', description='...')
        self.client.force_authenticate(user=self.user)
        
    def test_create_department(self):
        url = reverse('create_list_comment_view') 
        data = {
            "department": self.department.id, #REPLACE
                "author": self.user.id, #REPLACE
                "label": "REAL COMMENT",
                "body": "It is a body of a test comment",
                "tags": ["tag1", "tag2", "tag3"],
                "meta": {"this": "this",
                        "meta":"is tag"}
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['label'], "REAL COMMENT")

    def test_list_comments(self):
        Comment.objects.create(
            department= self.department, #REPLACE
                author= self.user, #REPLACE
                label= "REAL COMMENT",
                body= "It is a body of a test comment",
                tags= ["tag1", "tag2", "tag3"],
                meta= {"this": "this",
                        "meta":"is tag"}
        )
        Comment.objects.create(
            department= self.department, 
                author= self.user, 
                label= "REAL COMMENT 2",
                body= "It is a body of a test comment",
                tags= ["tag1", "tag2", "tag3"],
                meta= {"this": "this",
                        "meta":"is tag"}
        )
        url = reverse('create_list_comment_view') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(Comment.objects.count(), 1)