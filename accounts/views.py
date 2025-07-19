

from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
import logging

from .forms import (
    CustomAuthenticationForm,
    CustomUserCreationForm,
    UserUpdateForm,
)
from .models import CustomUser

logger = logging.getLogger(__name__)


def index(request):
    """Render the school's public landing page (index.html)."""
    return render(request, "index.html")

def departments(request):
    return render(request, 'departments.html')

def leadership(request):
    return render(request, 'leadership.html')

def admissions(request):
    return render(request, 'admissions.html')

def gallery(request):
    return render(request, 'gallery.html')


class CustomLoginView(LoginView):
    """Custom login that uses phone / username and pretty flash messages."""

    form_class   = CustomAuthenticationForm
    template_name = "accounts/login.html"

    def get_success_url(self):
        """
        Send the user to the school dashboard (`home`) after sign-in,
        unless a ?next=/some/url/ query-string was supplied.
        """
        return self.get_redirect_url() or reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Logged-in successfully. 🥳")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Invalid mobile number or password.")
        return super().form_invalid(form)
    
class RegisterView(CreateView):
    """Self‑service user sign‑up. Automatically logs‑in the fresh user."""

    form_class = CustomUserCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        # 1. Save user via the parent – this sets self.object
        response = super().form_valid(form)

        # 2. Re‑authenticate so Django attaches the *backend* attr
        raw_pwd = form.cleaned_data["password1"]
        user = authenticate(
            self.request,
            username=self.object.username,
            password=raw_pwd,
        )
        if user is not None:
            login(self.request, user)
            logger.info("New user %s automatically logged‑in after registration", user.username)
            messages.success(
                self.request,
                "Account created and logged‑in successfully. Welcome ✨",
            )
        else:
            # should never happen, but play safe
            messages.warning(
                self.request,
                "Account created – please sign‑in with your new credentials.",
            )
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error creating account. Please check the form.")
        return super().form_invalid(form)


@method_decorator(login_required, name="dispatch")
class UserListView(ListView):
    model = CustomUser
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    ordering = ["phone"]
    paginate_by = 20

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "current_session": "2025/2026",
                "current_term": "Term 1",
                "notification_count": 0,
                "total_users": CustomUser.objects.count(),
                "active_users": CustomUser.objects.filter(is_active=True).count(),
            }
        )
        logger.debug("User list context prepared (%s total)", ctx["total_users"])
        return ctx


@method_decorator(login_required, name="dispatch")
class UserUpdateView(UpdateView):
    model = CustomUser
    form_class = UserUpdateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("user_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "current_session": "2025/2026",
                "current_term": "Term 1",
                "notification_count": 0,
            }
        )
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"User {self.object.phone} updated successfully.")
        logger.info("User %s updated.", self.object.phone)
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error updating user. Please check the form.")
        logger.error("User update failed (%s): %s", self.kwargs["pk"], form.errors)
        return super().form_invalid(form)


@method_decorator(login_required, name="dispatch")
class UserDeleteView(DeleteView):
    model = CustomUser
    template_name = "accounts/user_confirm_delete.html"
    success_url = reverse_lazy("user_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "current_session": "2025/2026",
                "current_term": "Term 1",
                "notification_count": 0,
            }
        )
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f"User {self.object.phone} deleted successfully.")
        logger.info("User %s deleted.", self.object.phone)
        return super().form_valid(form)





