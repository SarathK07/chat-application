from django.contrib import admin
from .models import Message, Group, GroupMember, GroupMessage



# Register your models here.
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender','receiver','text','timestamp']

admin.site.register(Message,MessageAdmin)



class GroupAdmin(admin.ModelAdmin):
    list_display = ['id','name','created_by','created_at']
admin.site.register(Group, GroupAdmin)



class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ['group','user','joined_at']
admin.site.register(GroupMember,GroupMemberAdmin)


class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ['id','group','sender','text','timestamp']
admin.site.register(GroupMessage,GroupMessageAdmin)