from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.pagination import LimitOffsetPagination

from django.shortcuts import get_object_or_404, get_list_or_404

from .mixins import AuditLogMixin
from .serializers import DepartmentCommentSerializer, CommentAttachmentSerializer
from .models import AdminDepartmentComment, AdminCommentAttachment

#ADD PAFINATION AND FILTERING
class AdminDepartmentCommentView(AuditLogMixin, APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        comments = get_list_or_404(AdminDepartmentComment)
        serializer = DepartmentCommentSerializer(comments, many=True, context={"request":request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self,request):
        serializer = DepartmentCommentSerializer(data=request.data, context={"request":request})
        
        if serializer.is_valid():
            comment = serializer.save()
            self.comment_update(serializer, action="create_comment")
            return Response({
                "message": "Comment created successfully",
                "comment": serializer.data
                }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminCommentDetailView(AuditLogMixin, APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, comment_id):
        comment = get_object_or_404(AdminDepartmentComment, id=comment_id)
        serializer = DepartmentCommentSerializer(comment, context={"request":request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, comment_id):
        comment = get_object_or_404(AdminDepartmentComment, id=comment_id)
        serializer = DepartmentCommentSerializer(
            instance=comment,
            data = request.data,
            partial=True,
            context={"request":request}
        )
        if serializer.is_valid():
            comment = serializer.save()
            self.comment_update(serializer, action="update_comment")
            
            return Response({
                "message": "Comment updated successfully",
                "comment": serializer.data
                }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, comment_id):
        comment = get_object_or_404(
                AdminDepartmentComment, 
                id=comment_id
            )
        serializer = DepartmentCommentSerializer(comment, context={"request":request})
        self.comment_delete(comment, action="delete_comment")
        comment.delete()
        
        return Response({
                "message": "Comment removed successfully",
                "deleted_member": serializer.data
            }, status=status.HTTP_200_OK)
        
class CommentAttachmentsView(AuditLogMixin, APIView):
    permission_classes=[IsAdminUser]

    def get(self, request, comment_id):
        attachments = get_list_or_404(AdminCommentAttachment, comment_id=comment_id)
        serializer = CommentAttachmentSerializer(attachments, many=True, context={"request":request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self,request, comment_id):
        serializer = CommentAttachmentSerializer(data=request.data, context={"request":request})
        if serializer.is_valid():
            attachment = serializer.save()
            self.attachment_update(serializer, action="create_attachemnt")
            return Response({
                "message": "Comment attachment created succesfully",
                "attachment": serializer.data
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentAttachmentsDetailView(AuditLogMixin, APIView):
    permission_classes=[IsAdminUser]

    def delete(self, request, comment_id, attachment_id):
        attachment = get_object_or_404(
                AdminCommentAttachment, 
                id=attachment_id
            )
        serializer = CommentAttachmentSerializer(attachment, context={"request":request})
        self.attachment_delete(attachment, action="delete_attachemnt")
        attachment.delete()
        return Response({
                "message": "Attachment removed successfully",
                "deleted_member": serializer.data
            }, status=status.HTTP_200_OK)