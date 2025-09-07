from django.contrib import admin
from .models import(AuditLog,
                    VersionedSection,
                    DepartmentSection,
                    MediaAsset)

admin.site.register(DepartmentSection)
admin.site.register(MediaAsset)
admin.site.register(AuditLog)
admin.site.register(VersionedSection)