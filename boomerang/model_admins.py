from django.contrib import admin


class JobAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'start_time', 'elapsed_time', 'status', 'progress', 'goal',)
    list_display_links = None
    actions = None

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        """
        ie. remove permission to edit the job
        """
        pass
