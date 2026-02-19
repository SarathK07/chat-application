from django.shortcuts import render


def login_page(request):
    return render(request, "login.html")


def private_chat_page(request):
    return render(request, "private_chat.html")


def group_chat_page(request):
    return render(request, "group_chat.html")


def dashboard_page(request):
    return render(request, "dashboard.html")