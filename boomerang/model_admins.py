from django.contrib import admin

class JobAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'start_time', 'elapsed_time', 'status', 'progress', 'goal',
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
