import io
from django.urls import reverse
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from .models import Comment, AuditLog, CommentAttachment
from apps.core.tests.factories.user import UserFactory
from apps.core.tests.factories.department import DepartmentFactory
from apps.core.tests.factories.comment import CommentFactory, CommentAttachmentFactory


class AdminSetUpTest(APITestCase):
    def setUp(self):
        self.user = UserFactory(is_superuser=True, is_staff=True)
        self.client.force_authenticate(user=self.user)


class BaseAdminAppTest(AdminSetUpTest):
    def setUp(self):
        super().setUp()
        self.department = DepartmentFactory(chief=self.user)
        self.comments = CommentFactory.create_batch(
            2, department=self.department, author=self.user
        )

    def assertAuditLog(self, action):
        self.log = AuditLog.objects.last()
        self.assertIsNotNone(self.log)
        self.assertEqual(self.log.actor, self.user)
        self.assertEqual(self.log.department, self.department)
        self.assertEqual(self.log.action, action)


class CommentViewsTest(BaseAdminAppTest):
    def assertComment(self, response_data, comment):
        self.assertIsNotNone(response_data)
        self.assertEqual(str(response_data["author"]), str(comment.author.id))
        self.assertEqual(str(response_data["department"]), str(comment.department.id))
        self.assertEqual(response_data["label"], comment.label)
        self.assertEqual(response_data["tags"], comment.tags)
        self.assertEqual(response_data["meta"], comment.meta)
        self.assertEqual(response_data["body"], comment.body)

    def assertAuditLog(self, action, comment):
        super().assertAuditLog(action)
        self.assertComment(self.log.payload, comment)

    def test_create_comment(self):
        url = reverse("create_list_comment_view")
        payload = {
            "department": str(self.department.id),
            "author": str(self.user.id),
            "label": "NEW TEST COMMENT",
            "body": "It is a body of a test comment",
            "tags": ["tag1", "tag2"],
            "meta": {"key": "value"},
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        comment_instance = Comment.objects.get(id=response.data["id"])
        self.assertComment(response.data, comment_instance)
        self.assertAuditLog("create comment", comment_instance)

    def test_list_comments(self):
        url = reverse("create_list_comment_view")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comments = Comment.objects.all().order_by("-created_at")
        for resp_item, comment in zip(response.data, comments):
            self.assertComment(resp_item, comment)

    def test_retrieve_comment(self):
        comment = self.comments[0]
        url = reverse("comment_details_view", kwargs={"id": comment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertComment(response.data, comment)

    def test_update_comment(self):
        comment = self.comments[0]
        url = reverse("comment_details_view", kwargs={"id": comment.id})
        data = {"label": "UPDATED REAL COMMENT"}

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comment.refresh_from_db()
        self.assertComment(response.data, comment)
        self.assertAuditLog("update comment", comment)

    def test_delete_comment(self):
        comment = self.comments[0]
        url = reverse("comment_details_view", kwargs={"id": comment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertAuditLog("delete comment", comment)


class CommentAttachementsViewsTest(BaseAdminAppTest):
    def setUp(self):
        super().setUp()
        self.comment = self.comments[0]
        self.attachment = CommentAttachmentFactory(comment=self.comment)

        self.attachments_url = reverse(
            "comment_attachments_view", kwargs={"comment_id": self.comment.id}
        )
        self.detail_url = reverse(
            "atachments_detail_view",
            kwargs={"comment_id": self.comment.id, "id": self.attachment.id},
        )

    def assertAttachment(self, response_data, attachment):
        self.assertIsNotNone(response_data)
        self.assertEqual(str(response_data["comment"]), str(attachment.comment.id))
        self.assertEqual(response_data["meta"], attachment.meta)

    def assertAuditLog(self, action, attachment):
        super().assertAuditLog(action)
        self.assertAttachment(self.log.payload, attachment)

    def test_attachment_create(self):
        upload = SimpleUploadedFile(
            "file1.txt", b"hello world", content_type="text/plain"
        )
        payload = {
            "comment": str(self.comment.id),
            "file": upload,
            "filename": "file1.txt",
        }

        response = self.client.post(self.attachments_url, payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_attachment = CommentAttachment.objects.get(id=response.data["id"])
        self.assertAttachment(response.data, new_attachment)
        self.assertAuditLog("create commentattachment", new_attachment)

    def test_attachment_update(self):
        new_file = SimpleUploadedFile("new.txt", b"updated data")
        payload = {
            "comment": str(self.comment.id),
            "file": new_file,
            "filename": "new.txt",
        }

        response = self.client.patch(self.detail_url, payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.attachment.refresh_from_db()
        self.assertAttachment(response.data, self.attachment)
        self.assertAuditLog("update commentattachment", self.attachment)

    def test_atachment_delete(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertAuditLog("delete commentattachment", self.attachment)
