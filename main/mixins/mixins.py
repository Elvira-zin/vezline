from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        # анонім -> на логін, залогінений не staff -> 403
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()
