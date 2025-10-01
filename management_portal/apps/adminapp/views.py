from rest_framework.permissions import IsAdminUser
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .mixins import AuditLogMixin
from .serializers import CommentSerializer, CommentAttachmentSerializer
from .models import Comment, CommentAttachment


class CommentView(AuditLogMixin, ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class= LimitOffsetPagination
    filter_backends = [SearchFilter] 
    search_fields = ['author__email', 'author_role', 'department__slug']
    filterset_fields = {  
        'created_at': ['gte', 'lte'],
        'department_id': ['exact'],
        'label': ['icontains']
    }

    def perform_create(self, serializer):
        self.comment_update(serializer, action="create comment")
        return super().perform_create(serializer)

class CommentDetailView(AuditLogMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'id'

    def perform_update(self, serializer):
        self.comment_update(serializer, action="update comment")
        return super().perform_update(serializer)
    
    def perform_delete(self, serializer):
        self.comment_delete(serializer, action="delete comment")
        return super().perform_delete(serializer)
        
class CommentAttachmentsView(AuditLogMixin, ListCreateAPIView): 
    permission_classes= [IsAdminUser]
    queryset = CommentAttachment.objects.all()
    serializer_class = CommentAttachmentSerializer

    def perform_create(self, serializer):
        self.attachment_update(serializer, action="create attachment")
        return super().perform_create(serializer)

class CommentAttachmentsDetailView(AuditLogMixin, RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAdminUser]
    queryset = CommentAttachment.objects.all()
    serializer_class = CommentAttachmentSerializer
    lookup_field = 'id'
    
    def perform_update(self, serializer):
        self.attachment_update(serializer, action="update attachment")
        return super().perform_create(serializer)
    
    def perform_delete(self, serializer):
        self.attachment_delete(serializer, action="delete attachment")
        return super().perform_create(serializer)
