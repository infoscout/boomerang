from isc_admin import ModelAdmin

class JobAdmin(ModelAdmin):
    list_display = (
        'id', 'name', 'status', 'progress', 'goal',
    )
    # change_form_template = 'templates/view.html'

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False