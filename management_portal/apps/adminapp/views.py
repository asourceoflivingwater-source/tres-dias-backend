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

    def get_audit_payload(self, instance):
        payload = super().get_audit_payload(instance)
        payload.update({
            'label': instance.label,
            'body': instance.body,
        })
        return payload

class CommentDetailView(AuditLogMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'id'

    def get_audit_payload(self, instance):
        payload = super().get_audit_payload(instance)
        payload.update({
            'label': instance.label,
            'body': instance.body,
        })
        return payload
        
class CommentAttachmentsView(AuditLogMixin, ListCreateAPIView): 
    permission_classes= [IsAdminUser]
    queryset = CommentAttachment.objects.all()
    serializer_class = CommentAttachmentSerializer

    def get_audit_payload(self, instance):
        payload = super().get_audit_payload(instance)
        payload.update({
            'file_url': instance.file.url if instance.file else None,
            'filename': instance.filename,
            'comment_id': str(instance.comment_id),
        })
        return payload

class CommentAttachmentsDetailView(AuditLogMixin, RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAdminUser]
    queryset = CommentAttachment.objects.all()
    serializer_class = CommentAttachmentSerializer
    lookup_field = 'id'
    
    def get_audit_payload(self, instance):
        payload = super().get_audit_payload(instance)
        payload.update({
            'file_url': instance.file.url if instance.file else None,
            'filename': instance.filename,
            'comment_id': str(instance.comment_id),
        })
        return payload
