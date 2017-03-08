from django.contrib import admin


class JobAdmin(admin.ModelAdmin):

    change_list_template = 'admin/boomerang/change_list.html'
    list_display = ('id', 'name', 'start_time', 'elapsed_time', '_status', 'progress', 'goal',)
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

    def _status(self, obj):
        return '<span status-color="{status_color}">{status}</span>'.format(
            status_color=obj.status_color,
            status=obj.get_status_display()
        )
    _status.short_description = 'Status'
    _status.allow_tags = True
