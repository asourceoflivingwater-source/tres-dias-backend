from rest_framework.serializers import ModelSerializer
from .models import Comment, CommentAttachment

class StaffModelSerializer(ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not self.context.get('request').user.is_staff:
                    representation = None
        return representation

class CommentSerializer(StaffModelSerializer):

    class Meta:
        model = Comment
        fields = ["id", "department", "author", "author_role",
                "label", "body", "tags", "meta"]
        read_only_fields = ['id',]

class CommentAttachmentSerializer(StaffModelSerializer):

    class Meta:
        model = CommentAttachment
        fields = ["id", "comment", "file", "filename", "meta"]
        read_only_fields = ['id',]
    