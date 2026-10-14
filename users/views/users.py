from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from users.forms.auth import UserRegistrationForm
from users.forms.profile import ProfileUpdateForm


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            return redirect("login")
    else:
        form = UserRegistrationForm()

    return render(request, "users/register.html", {"form": form})

@login_required
def profile(request):
    return render(request, "users/profile.html")

@login_required
def profile_edit(request):
    if request.method == "POST":
        form = ProfileUpdateForm(
            request.POST,
            instance=request.user,
        )

        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(
        request,
        "users/profile_edit.html",
        {"form": form},
    )