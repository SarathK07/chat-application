from django.db import models
from accounts.models import User   # adjust import if needed
import uuid


class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages"
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.receiver}"
    



class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_groups"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GroupMember(models.Model):

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("member", "Member"),
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="members"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="group_memberships"
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="member"
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("group", "user")

    def __str__(self):
        return f"{self.user} in {self.group} ({self.role})"    

class GroupMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.group}"