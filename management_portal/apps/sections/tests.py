from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.department.models import Department
from unittest.mock import patch
from apps.department.models import DepartmentMember
from .models import (
    DepartmentSection,
    SectionPermission,
    VersionedSection,
    SectionStatus,
    VisibilityType,
    SectionType,
)
from apps.core.tests.factories.section import SectionFactory
from apps.department.tests import UserSetUpTest

User = get_user_model()


class TestUserSetup(UserSetUpTest):

    def setUp(self):
        super().setUp()
        self.section = SectionFactory(department=self.department)
        self.permission = SectionPermission.objects.create(
            section=self.section,
            role="chief",
            can_view=True,
            can_edit=True,
            can_publish=False,
        )
        VersionedSection.objects.create(
            section=self.section,
            version=1,
            content={"blocks": [{"text": "Initial Content"}]},
            published_by=self.users["admin"].user,
        )


class SectionAPITests(TestUserSetup, APITestCase):

    def setUp(self):
        super().setUp()
        self.list_url = reverse("sections_view")
        self.detail_url = reverse("section_edit_view", kwargs={"id": self.section.id})

    def test_admin_can_create_section(self):
        self.client.force_authenticate(user=self.users["admin"].user)
        data = {
            "department": self.department.id,
            "type": SectionType.TEAM_INFO,
            "title": "New Team Section",
            "visibility": VisibilityType.MEMBERS,
        }
        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DepartmentSection.objects.count(), 2)
        new_section = DepartmentSection.objects.last()
        self.assertEqual(new_section.status, SectionStatus.DRAFT)
        self.assertEqual(
            SectionPermission.objects.filter(section=new_section).count(), 6
        )

    @patch("apps.users.permissions.CanEditSection.has_permission", return_value=True)
    def test_allowed_user_can_update_section_draft_content(self, mock_permission):
        self.client.force_authenticate(user=self.users["chief"].user)
        new_draft = {"blocks": [{"type": "text", "text": "Updated Draft"}]}
        data = {"title": "New Title", "content_draft": new_draft}
        response = self.client.patch(self.detail_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.section.refresh_from_db()
        self.assertEqual(self.section.title, "New Title")
        self.assertEqual(self.section.content_draft, new_draft)


class CustomLogicAPITests(TestUserSetup, APITestCase):

    def setUp(self):
        super().setUp()
        self.section.content_draft = {
            "blocks": [{"type": "text", "text": "New Draft Content"}]
        }
        self.section.save()
        self.publish_url = reverse(
            "section_publish_view", kwargs={"id": self.section.id}
        )
        self.revert_url = reverse(
            "version_revert_view", kwargs={"section_id": self.section.id, "version": 1}
        )
        self.versions_url = reverse(
            "section_versions_view", kwargs={"section_id": self.section.id}
        )
        self.permission_edit_url = reverse(
            "section_permissions_edit_view", kwargs={"section_id": self.section.id}
        )
        self.section.status = SectionStatus.DRAFT
        self.section.published_at = None
        self.section.save()

    @patch("apps.users.permissions.CanPublishSection.has_permission", return_value=True)
    def test_publish_creates_new_version_and_updates_content(self, mock_permission):
        self.client.force_authenticate(user=self.users["admin"].user)
        data = {}
        response = self.client.patch(self.publish_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.section.refresh_from_db()
        self.assertEqual(self.section.status, SectionStatus.PUBLISHED)
        self.assertEqual(
            self.section.content_published,
            {"blocks": [{"type": "text", "text": "New Draft Content"}]},
        )
        self.assertEqual(self.section.content_draft, [])
        self.assertIsNotNone(
            self.section.published_at
        )  # Check that published_at is set
        self.assertEqual(self.section.published_by, self.users["admin"].user)
        self.assertEqual(
            VersionedSection.objects.filter(section=self.section).count(), 2
        )
        new_version = VersionedSection.objects.get(section=self.section, version=2)
        self.assertEqual(new_version.content, self.section.content_published)

    def test_publish_update_with_new_draft_content(self):
        self.client.force_authenticate(user=self.users["admin"].user)
        self.client.patch(self.publish_url, {})
        new_draft_content = {"blocks": [{"text": "Latest Content"}]}
        self.section.content_draft = new_draft_content
        self.section.status = SectionStatus.DRAFT  # Reset status for next publish
        self.section.save()

        response = self.client.patch(
            self.publish_url, {"content_draft": new_draft_content}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.section.refresh_from_db()

        self.assertEqual(self.section.content_published, new_draft_content)
        self.assertEqual(
            VersionedSection.objects.filter(section=self.section).count(), 3
        )

    def test_chief_can_update_section_permission_fields(self):
        self.client.force_authenticate(user=self.users["admin"].user)
        data = {
            "role": self.permission.role,
            "can_edit": False,  # Change a permission
            "can_publish": True,  # Change a permission
        }
        response = self.client.patch(self.permission_edit_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.permission.refresh_from_db()
        self.assertFalse(self.permission.can_edit)
        self.assertTrue(self.permission.can_publish)

    ## 6. SectionVersionRevertView (APIView - Requires IsAdminUser)

    def test_admin_can_revert_to_previous_version(self):
        # Setup: Create a newer version with different content
        current_content = {"blocks": [{"text": "Current Live Content"}]}
        self.section.content_published = current_content
        self.section.save()
        VersionedSection.objects.create(
            section=self.section,
            version=2,
            content=current_content,
            published_by=self.users["chief"].user,
        )

        self.client.force_authenticate(user=self.users["admin"].user)

        # Revert to version 1 (content: {'text': 'Initial Content'})
        response = self.client.post(self.revert_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.section.refresh_from_db()

        # Check that content_published is restored
        self.assertEqual(
            self.section.content_published, {"blocks": [{"text": "Initial Content"}]}
        )
        self.assertEqual(self.section.status, SectionStatus.PUBLISHED)
        # Check that published_by is the user performing the revert
        self.assertEqual(self.section.published_by, self.users["admin"].user)
