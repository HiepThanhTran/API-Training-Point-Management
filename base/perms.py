from rest_framework import permissions


class HasInGroup(permissions.IsAuthenticated):
    group_name = None

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_in_group(name=self.group_name)


class HasInSpeacialistGroup(HasInGroup):
    group_name = "specialist"


class HasInAssistantGroup(HasInGroup):
    group_name = "assistant"


class HasInStudentGroup(HasInGroup):
    group_name = "student"


class AllowedEditComment(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, comment):
        return super().has_permission(request, view) and request.user == comment.account
