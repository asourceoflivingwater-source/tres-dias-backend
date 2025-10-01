from rest_framework.serializers import ModelSerializer
from .models import Comment, CommentAttachment

class CommentSerializer(ModelSerializer):

    class Meta:
        model = Comment
        fields = ["id", "department", "author", "author_role",
                "label", "body", "tags", "meta"]
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if not self.context.get('request').user.is_staff:
            representation = None,
        
        return representation

class CommentAttachmentSerializer(ModelSerializer):

    class Meta:
        model = CommentAttachment
        fields = ["id", "comment", "file", "filename", "meta"]
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if not self.context.get('request').user.is_staff:
            representation = None,
        
        return representation