from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import DepartmentRole
from apps.core.tests.factories.section import SectionFactory
from apps.core.tests.factories.department import (
    DepartmentFactory,
    DepartmentMemberFactory,
)


class UserSetUpTest(APITestCase):
    def setUp(self):
        self.department = DepartmentFactory()
        self.users = {
            "admin": DepartmentMemberFactory(
                role="admin", user__is_superuser=True, user__is_staff=True
            ),
            "chief": DepartmentMemberFactory(role="chief", department=self.department),
            "assistant": DepartmentMemberFactory(
                role="assistant", department=self.department
            ),
            "team_member": DepartmentMemberFactory(
                role="team_member", department=self.department
            ),
            "viewer": DepartmentMemberFactory(
                role="viewer", department=self.department
            ),
        }


class DepartmentMemberTest(UserSetUpTest):
    def setUp(self):
        super().setUp()
        self.new_member = DepartmentMemberFactory()
        self.url = reverse(
            "department-members-view", kwargs={"department_id": self.department.id}
        )

    def test_add_member(self):
        data = {"user_email": self.new_member.email, "role": DepartmentRole.VIEWER}
        self.client.force_authenticate(user=self.users["team_member"].user)
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_member_admin(self):
        data = {"user_email": self.new_member.email, "role": DepartmentRole.VIEWER}
        self.client.force_authenticate(user=self.users["admin"].user)
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], data["role"])


class DepartmentSectionsTest(UserSetUpTest):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            "department_sections_view", kwargs={"slug": self.department.slug}
        )
        section_configs = [
            {"type": "HOME", "visibility": "public"},
            {"type": "TEAM-INFO", "visibility": "members"},
            {"type": "INTERACTIONS", "visibility": "members"},
            {
                "type": "CHIEF-INFO",
                "visibility": "role_based",
                "visible_for_roles": ["chief", "assistant"],
            },
            {
                "type": "TEAM_INFO",
                "visibility": "role_based",
                "visible_for_roles": ["team_member", "chief", "assistant", "secretary"],
            },
            {
                "type": "ASSISTANT_INFO",
                "visibility": "role_based",
                "visible_for_roles": ["chief", "assistant", "admin"],
            },
            {
                "type": "SECRETARY_INFO",
                "visibility": "role_based",
                "visible_for_roles": ["chief", "assistant", "admin"],
            },
        ]

        self.sections = [
            SectionFactory(department=self.department, **config)
            for config in section_configs
        ]

    def test_sections_anon(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_sections_admin(self):
        self.client.force_authenticate(user=self.users["admin"].user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 7)
        self.assertEqual(response.data[0]["title"], "Section 0")

    def test_sections_chief(self):
        self.client.force_authenticate(user=self.users["chief"].user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 7)

    def test_sections_member(self):
        self.client.force_authenticate(user=self.users["team_member"].user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        visible_types = [item["type"] for item in response.data]
        self.assertIn("TEAM_INFO", visible_types)
