import io
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from apps.users.models import User
from apps.department.models import Department
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Comment, AuditLog, CommentAttachment

class BaseAdminAppTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345', is_staff=True)
        self.department = Department.objects.create(title='test_department', 
            chief=self.user, 
            slug='test-department', 
            description='...')
        self.comment = Comment.objects.create(
            department=self.department,
            author=self.user,
            label="REAL COMMENT",
            body="Initial comment body",
            tags=["tag1", "tag2", "tag3"],
            meta={"this": "this", "meta": "is tag"},
        )
        self.client.force_authenticate(user=self.user)
        
class CommentViewsTest(BaseAdminAppTest):
    def test_create_comment(self):
        url = reverse('create_list_comment_view') 
        data = {
            "department": self.department.id, 
                "author": self.user.id, 
                "label": "REAL COMMENT",
                "body": "It is a body of a test comment",
                "tags": ["tag1", "tag2", "tag3"],
                "meta": {"this": "this",
                        "meta":"is tag"}
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['label'], "REAL COMMENT")

        log = AuditLog.objects.last()
        self.assertIsNotNone(log)
        self.assertEqual(log.actor, self.user)
        self.assertEqual(log.department, self.department)
        self.assertEqual(log.action, "create comment")

        payload = log.payload
        self.assertEqual(payload["model"], "Comment")
        self.assertIn("label", payload)
        self.assertEqual(payload["label"], "REAL COMMENT")

    def test_list_comments(self):
        Comment.objects.create(
            department= self.department, 
                author= self.user, 
                label= "SECOND REAL COMMENT",
                body= "It is a body of a test comment",
                tags= ["tag1", "tag2", "tag3"],
                meta= {"this": "this",
                        "meta":"is tag"}
        )
        
        url = reverse('create_list_comment_view') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(Comment.objects.count(), 1)
    
    def test_retrieve_comment(self):
        url = reverse('comment_details_view', kwargs={'id': self.comment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['label'], "REAL COMMENT")
    
    def test_update_comment(self):
        url = reverse('comment_details_view', kwargs={'id': self.comment.id})
        data = {
                'label': 'UPDATED REAL COMMENT',     
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['label'], "UPDATED REAL COMMENT")

        log = AuditLog.objects.last()
        self.assertEqual(log.action, "update comment")
        self.assertEqual(log.payload["label"], "UPDATED REAL COMMENT")
    
    def test_delete_comment(self):
        
        url = reverse('comment_details_view', kwargs={'id': self.comment.id})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        log = AuditLog.objects.last()
        self.assertEqual(log.action, "delete comment")
        self.assertEqual(log.payload["label"], "REAL COMMENT")

class CommentAttachementsViewsTest(BaseAdminAppTest):
    def setUp(self):
        super().setUp()
        self.attachments_url = reverse(
            "comment_attachments_view", kwargs={"comment_id": self.comment.id}
        )
     
    def test_attachment_create(self):
        file_content = io.BytesIO(b"hello world")
        upload = SimpleUploadedFile("file1.txt", file_content.read(), content_type="text/plain")

        response = self.client.post(
            self.attachments_url,
            {"comment": str(self.comment.id), "file": upload, "filename": "file1.txt"},
            format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        log = AuditLog.objects.last()
        self.assertIsNotNone(log)
        self.assertEqual(log.actor, self.user)
        self.assertEqual(log.action, "create commentattachment")
        self.assertEqual(log.department, self.department)
        self.assertEqual(log.payload["model"], "CommentAttachment")
        self.assertEqual(log.payload["filename"], "file1.txt")
    
    def test_attachment_update(self):
        file_obj = SimpleUploadedFile("old.txt", b"data")
        attachment = CommentAttachment.objects.create(
            comment=self.comment, file=file_obj, filename="old.txt"
        )

        detail_url = reverse(
            "atachments_detail_view",
            kwargs={"comment_id": self.comment.id, "id": attachment.id},
        )

        new_file = SimpleUploadedFile("new.txt", b"updated data")

        response = self.client.patch(
            detail_url,
            {"comment": str(self.comment.id), "file": new_file, "filename": "new.txt"},
            format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        log = AuditLog.objects.last()
        self.assertEqual(log.action, "update commentattachment")
        self.assertEqual(log.payload["filename"], "new.txt")
        self.assertEqual(log.department, self.department)

    def test_atachment_delete(self):
        file_obj = SimpleUploadedFile("delete.txt", b"temporary data")
        attachment = CommentAttachment.objects.create(
            comment=self.comment, file=file_obj, filename="delete.txt"
        )

        detail_url = reverse(
            "atachments_detail_view",
            kwargs={"comment_id": self.comment.id, "id": attachment.id},
        )

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        log = AuditLog.objects.last()
        self.assertEqual(log.action, "delete commentattachment")
        self.assertEqual(log.payload["filename"], "delete.txt")
        self.assertEqual(log.department, self.department)   