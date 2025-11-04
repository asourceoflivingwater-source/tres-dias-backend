from .models import AuditLog
from rest_framework.permissions import IsAdminUser
import uuid
class AuditLogMixin:
    def create_audit_log(self, action, department, section=None, payload=None):
        "Создает запись аудита"
        AuditLog.objects.create(
            actor=self.request.user,
            department=department,
            section=section or None,
            action=action,
            payload=payload or {}
        )

    def get_audit_department(self, instance):
        """Извлекает объект Department из инстанса. Должен быть переопределен при необходимости."""
        # Для Comment: инстанс.department
        # Для CommentAttachment: инстанс.comment.department
        
        if hasattr(instance, 'department'):
            return instance.department
        elif hasattr(instance, 'comment') and hasattr(instance.comment, 'department'):
            return instance.comment.department
        return None
    
    def get_audit_payload(self, instance):
        payload = {
            'id': str(getattr(instance, 'id', None)),
            'model': instance.__class__.__name__,
            }
        extra_fields = getattr(self, "audit_fields", [])
        for field in extra_fields:
            value = getattr(instance, field, None)
            # Handle related objects and UUIDs safely
            if isinstance(value, uuid.UUID):
                value = str(value)
            elif hasattr(value, "id"):  # related model
                value = str(value.id)
            payload[field] = value
        return payload
    
    def perform_create(self, serializer):
        # 1. Выполнить создание объекта
        instance = serializer.save()
        super().perform_create(serializer)
        
        # 2. Аудит после создания
        department = self.get_audit_department(instance)
        payload = self.get_audit_payload(instance)
        self.create_audit_log(f"create {instance.__class__.__name__.lower()}", department, payload=payload)

    def perform_update(self, serializer):
        # 1. Выполнить обновление объекта
        super().perform_update(serializer)
        instance = serializer.instance
        
        # 2. Аудит после обновления
        department = self.get_audit_department(instance)
        payload = self.get_audit_payload(instance)
        self.create_audit_log(f"update {instance.__class__.__name__.lower()}", department, payload=payload)

    def perform_destroy(self, instance):
        # 1. Аудит ДО удаления (чтобы иметь доступ к полям)
        department = self.get_audit_department(instance)
        payload = self.get_audit_payload(instance)
        self.create_audit_log(f"delete {instance.__class__.__name__.lower()}", department, payload=payload)
        
        # 2. Выполнить удаление объекта
        super().perform_destroy(instance)



class AdminViewMixin(AuditLogMixin):
    permission_classes = [IsAdminUser]
    model = None

    @property
    def queryset(self):
        assert self.model is not None, (
            f"{self.__class__.__name__} must define a 'model' attribute or override 'queryset'."
        )
        return self.model.objects.all()