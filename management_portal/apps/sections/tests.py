from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch
from django.utils import timezone

from apps.department.models import DepartmentMember

from .models import (
    DepartmentSection, SectionPermission, VersionedSection, 
    SectionStatus, VisibilityType, SectionType
)
# Assuming these imports and the classes they represent are correct
# from apps.users.permissions import CanEditSection, CanPublishSection, IsChief 
# from apps.department.models import Department, DepartmentRole (Needed for FK/Choices)

User = get_user_model()

# --- Mock Foreign Key Setup ---

class TestUserSetup(TestCase):
    """
    Sets up common users, a Department, and initial Section/Permissions for testing.
    """
    def setUp(self):
        # Create a mock Department (required by DepartmentSection and MediaAsset)
        # Note: You'll need to define a mock Department class if it's not available 
        # in the test environment, or use a real one. Assuming a mock/real one exists:
        from apps.department.models import Department
        self.department = Department.objects.create(title='Test Dept', slug='test-dep')
    
       
        # Users
        self.admin_user = User.objects.create_user(
            username='adminuser', email='admin@example.com', password='password123', is_staff=True, is_superuser=True
        )
        self.chief_user = User.objects.create_user(
            username='chiefuser', email='chief@example.com', password='password123', is_staff=False
        )
        self.regular_user = User.objects.create_user(
            username='regularuser', email='regular@example.com', password='password123', is_staff=False
        )
        DepartmentMember.objects.create(
            user=self.chief_user, 
            role='chief', 
            department=self.department
        )
        # Section instance for detail views
        self.section = DepartmentSection.objects.create(
            department=self.department,
            type=SectionType.HOME,
            title='Test Section', 
            status=SectionStatus.DRAFT,
            content_draft={'blocks': []},
            content_published={},
            updated_by=self.admin_user,
        )
        
        # Permission instance setup (using the new fields)
        # Assuming 'chief' is a valid choice in DepartmentRole.choices
        self.permission = SectionPermission.objects.create(
            section=self.section,
            # Assuming 'chief' is a valid role string
            role='chief', 
            can_view=True,
            can_edit=True,
            can_publish=False
        )
        
        # Version instance
        VersionedSection.objects.create(
            section=self.section,
            version=1,
            content={'blocks': [{'text': 'Initial Content'}]},
            published_by=self.admin_user
        )


# --- Test Suite for Core API Endpoints ---

class SectionAPITests(TestUserSetup, APITestCase):

    def setUp(self):
        super().setUp()
        self.list_url = reverse('sections_view')
        self.detail_url = reverse('section_edit_view', kwargs={'id': self.section.id})

    ## 1. SectionsView (ListCreateAPIView - Requires IsAdminUser)
    
    def test_admin_can_create_section(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'department': self.department.id,
            'type': SectionType.TEAM_INFO,
            'title': 'New Team Section',
            'visibility': VisibilityType.MEMBERS,
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DepartmentSection.objects.count(), 2)
        new_section = DepartmentSection.objects.last()
        # Verify read-only/default fields
        self.assertEqual(new_section.status, SectionStatus.DRAFT)
        # visible_for_roles should be an empty list by default
        self.assertEqual(new_section.visible_for_roles, []) 

    ## 2. SectionDetailView (RetrieveUpdateDestroyAPIView - Requires CanEditSection)
    
    @patch('apps.users.permissions.CanEditSection.has_permission', return_value=True)
    def test_allowed_user_can_update_section_draft_content(self, mock_permission):
        self.client.force_authenticate(user=self.chief_user)
        new_draft = {'blocks': [{'type': 'text', 'text': 'Updated Draft'}]}
        data = {'title': 'New Title', 'content_draft': new_draft}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.section.refresh_from_db()
        self.assertEqual(self.section.title, 'New Title')
        self.assertEqual(self.section.content_draft, new_draft)
    
# --- Test Suite for Custom Logic ---

class CustomLogicAPITests(TestUserSetup, APITestCase):
    
    def setUp(self):
        super().setUp()
        self.section.content_draft = {'blocks': [{'type': 'text', 'text': 'New Draft Content'}]}
        self.section.save()
        self.publish_url = reverse('section_publish_view', kwargs={'id': self.section.id})
        self.revert_url = reverse('version_revert_view', kwargs={'section_id': self.section.id, 'version': 1})
        self.versions_url = reverse('section_versions_view', kwargs={'section_id': self.section.id})
        self.permission_edit_url = reverse('section_permissions_edit_view', 
                                          kwargs={'section_id': self.section.id})
        # Ensure section is not published initially
        self.section.status = SectionStatus.DRAFT
        self.section.published_at = None
        self.section.save()
        

    ## 3. SectionsPublishView (UpdateAPIView - Requires CanPublishSection)
    
    @patch('apps.users.permissions.CanPublishSection.has_permission', return_value=True)
    def test_publish_creates_new_version_and_updates_content(self, mock_permission):
        self.client.force_authenticate(user=self.admin_user)
        data = {} 
        response = self.client.patch(self.publish_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.section.refresh_from_db()
        
        # Check that the section status, content, and timestamp are updated
        self.assertEqual(self.section.status, SectionStatus.PUBLISHED)
        self.assertEqual(self.section.content_published, {'blocks': [{'type': 'text', 'text': 'New Draft Content'}]})
        self.assertEqual(self.section.content_draft, [])
        self.assertIsNotNone(self.section.published_at) # Check that published_at is set
        self.assertEqual(self.section.published_by, self.admin_user)

        # Check that a new version is created (version 2)
        self.assertEqual(VersionedSection.objects.filter(section=self.section).count(), 2)
        new_version = VersionedSection.objects.get(section=self.section, version=2)
        self.assertEqual(new_version.content, self.section.content_published)
        
    
    def test_publish_update_with_new_draft_content(self):
        # Setup: Ensure user has permission to publish (admin/chief)
        self.client.force_authenticate(user=self.admin_user)
        
        # Create a new version 2 (published content)
        self.client.patch(self.publish_url, {})
        
        # Update the draft content for the next publish (version 3)
        new_draft_content = {'blocks': [{'text': 'Latest Content'}]}
        self.section.content_draft = new_draft_content
        self.section.status = SectionStatus.DRAFT # Reset status for next publish
        self.section.save()
        
        # Publish again, passing the new draft content explicitly (optional but good to test)
        response = self.client.patch(self.publish_url, {'content_draft': new_draft_content}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.section.refresh_from_db()
        
        # Verify published content is the new draft
        self.assertEqual(self.section.content_published, new_draft_content)
        # Verify version count is 3
        self.assertEqual(VersionedSection.objects.filter(section=self.section).count(), 3)


    ## 4. SectionPermissionEditView (UpdateAPIView - Requires IsAdminUser|IsChief)

    def test_chief_can_update_section_permission_fields(self):
        self.client.force_authenticate(user=self.chief_user)
        data = {
            'role': self.permission.role, 
            'can_edit': False, # Change a permission
            'can_publish': True # Change a permission
        }
        response = self.client.patch(self.permission_edit_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.permission.refresh_from_db()
        self.assertFalse(self.permission.can_edit)
        self.assertTrue(self.permission.can_publish)
        
        # Check if the DepartmentSection object was synced via the SectionPermission save() method
        self.section.refresh_from_db()
        self.assertIn('chief', self.section.allow_publish_roles)
        self.assertNotIn('chief', self.section.allow_edit_roles)


    ## 6. SectionVersionRevertView (APIView - Requires IsAdminUser)
    
    def test_admin_can_revert_to_previous_version(self):
        # Setup: Create a newer version with different content
        current_content = {'blocks': [{'text': 'Current Live Content'}]}
        self.section.content_published = current_content
        self.section.save()
        VersionedSection.objects.create(
            section=self.section, version=2, content=current_content, published_by=self.chief_user
        )

        self.client.force_authenticate(user=self.admin_user)
        
        # Revert to version 1 (content: {'text': 'Initial Content'})
        response = self.client.post(self.revert_url) 
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.section.refresh_from_db()
        
        # Check that content_published is restored
        self.assertEqual(self.section.content_published, {'blocks': [{'text': 'Initial Content'}]})
        self.assertEqual(self.section.status, SectionStatus.PUBLISHED)
        # Check that published_by is the user performing the revert
        self.assertEqual(self.section.published_by, self.admin_user)