from .models import AuditLog

class AuditLogMixin:
    def create_audit_log(self, action, department, section = None, payload=None):

        AuditLog.objects.create(
            actor=self.request.user,
            department=department,
            section=section or None,
            action=action,
            payload=payload or {}
        )

    def comment_update(self, serializer, action):
        
        instance= serializer.save()
        department = instance.department
        payload={
            'label': instance.label,
            'body' :instance.body
        }
        self.create_audit_log(action, department, payload=payload)
        
        return instance
    
    def comment_delete(self, instance, action):
        department = instance.department
        payload = {
            'label': instance.label,
            'body': instance.body
        }
        self.create_audit_log(action, department, payload=payload)
    
    def attachment_update(self, serializer, action):
        instance=serializer.save()
        department = instance.comment.department
        payload={
            'file': instance.file.url,
            'filename' :instance.filename
        }
        self.create_audit_log(action, department, payload=payload)
    
    def attachment_delete(self, instance, action):
        department = instance.comment.department
        payload = {
            'file': instance.file.url,
            'filename' :instance.filename
        }
        self.create_audit_log(action, department, payload=payload)
        
