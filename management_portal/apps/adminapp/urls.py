from django.urls import path
from .views import (CommentView, 
                    CommentDetailView,
                    CommentAttachmentsView,
                    CommentAttachmentsDetailView)

urlpatterns=[
    path("admin/department-comments/", CommentView.as_view(), name="create_list_comment_view"),
    path("admin/department-comments/<uuid:id>/", CommentDetailView.as_view(), name="comment_details_view"),
    path("admin/department-comments/<uuid:comment_id>/attachments/", 
        CommentAttachmentsView.as_view(), name="comment_attachments_view"),
    path("admin/department-comments/<uuid:comment_id>/attachments/<uuid:attachment_id>/",
        CommentAttachmentsDetailView.as_view(), name="atachments_detail_view"),
    
]