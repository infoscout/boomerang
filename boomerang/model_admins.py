from isc_admin import ModelAdmin

class JobAdmin(ModelAdmin):
	list_display = (
        'id', 'name', 'status', 'progress', 'goal',
    )
    