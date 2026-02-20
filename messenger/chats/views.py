from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import uuid
from .models import Message, Group, GroupMember, GroupMessage
from accounts.models import User


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sender = request.user  # comes from JWT (UUID user)
        receiver_id = request.data.get("receiver_id")
        text = request.data.get("text")

        if not receiver_id or not text:
            return Response(
                {"error": "receiver_id and text are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Validate UUID
        try:
            receiver_uuid = uuid.UUID(receiver_id)
        except ValueError:
            return Response(
                {"error": "Invalid receiver_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        receiver = get_object_or_404(User, id=receiver_uuid)

        Message.objects.create(
            sender=sender,
            receiver=receiver,
            text=text
        )

        return Response(
            {"message": "Message sent successfully"},
            status=status.HTTP_201_CREATED
        )


class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        other_user_id = request.query_params.get("user_id")

        if not other_user_id:
            return Response(
                {"error": "user_id query param is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Validate UUID
        try:
            other_user_uuid = uuid.UUID(other_user_id)
        except ValueError:
            return Response(
                {"error": "Invalid user_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        messages = Message.objects.filter(
            sender_id__in=[user.id, other_user_uuid],
            receiver_id__in=[user.id, other_user_uuid]
        ).order_by("timestamp")

        return Response([
            {
                "sender_id": str(msg.sender.id),
                "sender": msg.sender.username,
                "text": msg.text,
                "time": msg.timestamp
            }
            for msg in messages
        ], status=status.HTTP_200_OK)
    

class CreateGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get("name")

        if not name:
            return Response({"error": "Group name required"}, status=400)

        group = Group.objects.create(
            name=name,
            created_by=request.user
        )

        # Creator becomes admin
        GroupMember.objects.create(
            group=group,
            user=request.user,
            role="admin"
        )

        return Response({
            "group_id": str(group.id),
            "group_name": group.name,
            "created_by": request.user.username,
            "role": "Group Admin"
        }, status=201)        

class AddGroupMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        group_id = request.data.get("group_id")
        user_id = request.data.get("user_id")

        group = get_object_or_404(Group, id=group_id)

        # Check if requester is admin
        is_admin = GroupMember.objects.filter(
            group=group,
            user=request.user,
            role="admin"
        ).exists()

        if not is_admin:
            return Response(
                {"error": "Only Group Admin can add members"},
                status=403
            )

        user = get_object_or_404(User, id=user_id)

        membership, created = GroupMember.objects.get_or_create(
            group=group,
            user=user,
            defaults={"role": "member"}
        )

        if not created:
            return Response(
                {"message": "User already a member"},
                status=200
            )

        return Response({
            "group_id": str(group.id),
            "group_name": group.name,
            "member_added": user.username,
            "member_role": "Member",
            "added_by": f"{request.user.username} (Group Admin)",
            "added_at": membership.joined_at.isoformat()
        }, status=201)    


class RemoveGroupMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        group_id = request.data.get("group_id")
        user_id = request.data.get("user_id")

        group = get_object_or_404(Group, id=group_id)

        is_admin = GroupMember.objects.filter(
            group=group,
            user=request.user,
            role="admin"
        ).exists()

        if not is_admin:
            return Response(
                {"error": "Only Group Admin can remove members"},
                status=403
            )

        membership = get_object_or_404(
            GroupMember,
            group=group,
            user_id=user_id
        )

        # Prevent removing admin
        if membership.role == "admin":
            return Response(
                {"error": "Admin cannot be removed"},
                status=400
            )

        removed_user = membership.user.username
        membership.delete()

        return Response({
            "group_name": group.name,
            "removed_member": removed_user,
            "removed_by": f"{request.user.username} (Group Admin)"
        })



class SendGroupMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        group_id = request.data.get("group_id")
        text = request.data.get("text")

        group = get_object_or_404(Group, id=group_id)

        is_member = GroupMember.objects.filter(
            group=group,
            user=request.user
        ).exists()

        if not is_member:
            return Response(
                {"error": "You are not a member of this group"},
                status=403
            )

        GroupMessage.objects.create(
            group=group,
            sender=request.user,
            text=text
        )

        return Response({"message": "Message sent"})
    


class GroupChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        group_id = request.query_params.get("group_id")

        group = get_object_or_404(Group, id=group_id)

        if not GroupMember.objects.filter(
            group=group,
            user=request.user
        ).exists():
            return Response({"error": "Access denied"}, status=403)

        messages = group.messages.select_related("sender").order_by("timestamp")

        return Response([
    {
        "sender": (
            f"{msg.sender.username} (Group Admin)"
            if GroupMember.objects.filter(
                group=group,
                user=msg.sender,
                role="admin"
            ).exists()
            else msg.sender.username
        ),
        "sender_id": str(msg.sender.id),
        "text": msg.text,
        "time": msg.timestamp
    }
    for msg in messages
])
    
class MyGroupsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = GroupMember.objects.filter(user=request.user)

        return Response([
            {
                "id": str(m.group.id),
                "name": m.group.name,
                "is_admin": m.group.created_by == request.user
            }
            for m in memberships
        ])
    

    from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Group, GroupMember


class GroupMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):

        group = get_object_or_404(Group, id=group_id)

        # Check if user is member
        if not GroupMember.objects.filter(group=group, user=request.user).exists():
            return Response({"error": "Not a group member"}, status=403)

        members = GroupMember.objects.filter(group=group)

        data = []
        for member in members:
            data.append({
                "id": str(member.user.id),
                "username": member.user.username,
                "is_admin": group.created_by == member.user
            })

        return Response(data)
    

from django.db.models import Q

class RecentChatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        messages = Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).order_by("-timestamp")

        users = set()

        for msg in messages:
            if msg.sender != user:
                users.add(msg.sender)
            if msg.receiver != user:
                users.add(msg.receiver)

        data = [
            {
                "id": str(u.id),
                "username": u.username
            }
            for u in users
        ]

        return Response(data)
