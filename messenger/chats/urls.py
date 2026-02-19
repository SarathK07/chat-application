from django.urls import path
from .views import SendMessageView, ChatHistoryView, CreateGroupView, AddGroupMemberView, SendGroupMessageView, GroupChatHistoryView, RemoveGroupMemberView, MyGroupsView, GroupMembersView,RecentChatsView


urlpatterns = [
    path("send/", SendMessageView.as_view()),
    path("history/", ChatHistoryView.as_view()),
    path("groups/create/",CreateGroupView.as_view()),
    path("groups/add-member/", AddGroupMemberView.as_view()),
    path("groups/send-message/", SendGroupMessageView.as_view()),
    path("groups/history/", GroupChatHistoryView.as_view()),
    path("groups/remove/", RemoveGroupMemberView.as_view()),
    path("groups/my-groups/", MyGroupsView.as_view()),
    path("recent/", RecentChatsView.as_view()),


    path("groups/<uuid:group_id>/members/", GroupMembersView.as_view()),
]
