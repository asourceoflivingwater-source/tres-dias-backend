from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .mixins import AdminViewMixin
from .serializers import CommentSerializer, CommentAttachmentSerializer
from .models import Comment, CommentAttachment

class CommentView(AdminViewMixin, ListCreateAPIView):
    serializer_class = CommentSerializer
    model = Comment
    pagination_class= LimitOffsetPagination
    filter_backends = [SearchFilter] 
    search_fields = ['author__email', 'author_role', 'department__slug']
    audit_fields = ['label', 'body']
    filterset_fields = {  
        'created_at': ['gte', 'lte'],
        'department_id': ['exact'],
        'label': ['icontains']
    }

class CommentDetailView(AdminViewMixin, RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    model = Comment
    audit_fields = ['label', 'body']
    lookup_field = 'id'
        
class CommentAttachmentsView(AdminViewMixin, ListCreateAPIView): 
    serializer_class = CommentAttachmentSerializer
    model = CommentAttachment
    audit_fields = ['file_url', 'filename', 'comment_id']

class CommentAttachmentsDetailView(AdminViewMixin, RetrieveUpdateDestroyAPIView):
    serializer_class = CommentAttachmentSerializer
    model = CommentAttachment
    lookup_field = 'id'
    audit_fields = ['file_url', 'filename', 'comment_id']

