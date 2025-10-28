from .models import AuditLog

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
        """Создает полезную нагрузку для записи аудита. Должен быть переопределен во вьюхах, если нужна кастомная логика."""
        return {
            'id': str(getattr(instance, 'id', None)),
            'model': instance.__class__.__name__,
            # Добавьте другие общие поля или просто верните {}
        }
    
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
