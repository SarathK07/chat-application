from django.urls import path
from .views import login_page, private_chat_page, group_chat_page, dashboard_page

urlpatterns = [
    path('', login_page, name="login_page"),
    path('chat/', private_chat_page, name="private_chat"),
    path('group/', group_chat_page, name="group_chat"),
    path("dashboard/", dashboard_page, name="dashboard"),
    ]
