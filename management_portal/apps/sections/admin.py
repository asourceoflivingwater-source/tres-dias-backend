from django.contrib import admin
from .models import(VersionedSection,
                    DepartmentSection,
                    MediaAsset,
                    SectionPermission)

admin.site.register(DepartmentSection)
admin.site.register(MediaAsset)
admin.site.register(VersionedSection)
admin.site.register(SectionPermission)