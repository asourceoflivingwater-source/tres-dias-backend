from django.urls import path
from .views import (AdminDepartmentCommentView, 
                    AdminCommentDetailView,
                    CommentAttachmentsView,
                    CommentAttachmentsDetailView)

urlpatterns=[
    path("admin/department-comments/", AdminDepartmentCommentView.as_view(), name="create_list_comment_view"),
    path("admin/department-comments/<uuid:comment_id>/", AdminCommentDetailView.as_view(), name="comment_details_view"),
    path("admin/department-comments/<uuid:comment_id>/attachments/", 
        CommentAttachmentsView.as_view(), name="comment_attachments_view"),
    path("admin/department-comments/<uuid:comment_id>/attachments/<uuid:attachment_id>/",
        CommentAttachmentsDetailView.as_view(), name="atachments_detail_view"),
    
]