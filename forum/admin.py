from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from forum.models import Category, Thread, Post


class CustomUserAdmin(UserAdmin):
    """Redesigns the default user administration."""
    fields = ['password']


class CategoryAdmin(admin.ModelAdmin):
    fields = ['title_plain']


class ThreadAdmin(admin.ModelAdmin):
    """Thread layout in the admin control panel."""
# Actions
    def admin_lock(self, request, queryset):
        rows_updated = queryset.update(is_locked=True)
        if rows_updated == 1:
            message_bit = "1 thread was"
        else:
            message_bit = "%s threads were" % rows_updated
        self.message_user(request, "%s successfully marked as locked" % message_bit)
    admin_lock.short_description = "Lock selected threads"

    def admin_unlock(self, request, queryset):
        rows_updated = queryset.update(is_locked=False)
        if rows_updated == 1:
            message_bit = "1 thread was"
        else:
            message_bit = "%s threads were" % rows_updated
        self.message_user(request, "%s successfully marked as unlocked" % message_bit)
    admin_unlock.short_description = "Unlock selected threads"

    def admin_remove(self, request, queryset):
        rows_updated = queryset.update(is_removed=True)
        if rows_updated == 1:
            message_bit = "1 thread was"
        else:
            message_bit = "%s threads were" % rows_updated
        self.message_user(request, "%s successfully marked as removed" % message_bit)
    admin_remove.short_description = "Remove selected threads"

    def admin_restore(self, request, queryset):
        rows_updated = queryset.update(is_removed=False)
        if rows_updated == 1:
            message_bit = "1 thread was"
        else:
            message_bit = "%s threads were" % rows_updated
            self.message_user(request, "%s successfully marked as restored" % message_bit)
    admin_restore.short_description = "Restore selected threads"

    actions = ['admin_lock', 'admin_unlock',
               'admin_remove', 'admin_restore']
#    fieldsets = [
#        (None, {'fields': ['title']}),
#        (None, {'fields': ['author']}),
#        (None, {'fields': ['category']}),
#        (None, {'fields': ['creation_date']}),
#        (None, {'fields': ['latest_reply_date']}),
#        (None, {'fields': ['is_locked']}),
#        (None, {'fields': ['is_removed']}),
#        (None, {'fields': ['bookmarker'],
#                'classes': ['collapse']}),
#        (None, {'fields': ['subscriber'],
#                'classes': ['collapse']}),
#        (None, {'fields': ['hider'],
#                'classes': ['collapse']}),
#        (None, {'fields': ['threadmin'],
#                'classes': ['collapse']}),
#    ]
    date_hierarchy =  'creation_date'
    list_display   = ('title_html', 'category', 'author',
                      'relative_date', 'creation_date')
    list_filter    = ('category',) # Doesn't work
    search_fields  = ['title_html', 'author']


class PostAdmin(admin.ModelAdmin):
    """Post layout in the admin control panel."""
# Actions
    def admin_remove(self, request, queryset):
        rows_updated = queryset.update(is_removed=True)
        if rows_updated == 1:
            message_bit = "1 post was"
        else:
            message_bit = "%s posts were" % rows_updated
        self.message_user(request, "%s successfully marked as removed" % message_bit)
    admin_remove.short_description = "Remove selected posts"

    def admin_restore(self, request, queryset):
        rows_updated = queryset.update(is_removed=False)
        if rows_updated == 1:
            message_bit = "1 post was"
        else:
            message_bit = "%s posts were" % rows_updated
        self.message_user(request, "%s successfully marked as restored" % message_bit)
    admin_restore.short_description = "Restore selected threads"

    actions = ['admin_remove', 'admin_restore']
#    fieldsets = [
#        (None, {'fields': ['author']}),
#        (None, {'fields': ['thread']}),
#        (None, {'fields': ['creation_date']}),
#        (None, {'fields': ['content'],
#                'classes': ['collapse']}),
#        (None, {'fields': ['is_removed']}),
#        (None, {'fields': ['co-editor'],
#                'classes': ['collapse']}),
#        (None, {'fields': ['agrees'],
#                'classes': ['collapse']}),
#        (None, {'fields': ['thanks'],
#                'classes': ['collapse']}),
#        (None, {'fields': ['saves'],
#                'classes': ['collapse']}),
#    ]
    date_hierarchy =  'creation_date'
    list_display   = ('thread', 'author',
                      'relative_date', 'creation_date')
    list_filter    = ('thread',)
    search_fields  = ['thread', 'author']

# admin.site.register(Category, CategoryAdmin)
# admin.site.register(Thread, ThreadAdmin)
# admin.site.register(Post, PostAdmin)

# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)
