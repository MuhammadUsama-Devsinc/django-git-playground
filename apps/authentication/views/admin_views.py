from django.contrib.auth import authenticate
from django.shortcuts import redirect, render
from django.views import View
from ..forms import AdminAuthenticationFormWithOTP, OTPVerificationForm
from ..mixins import AdminContextMixin
from ..models import User
from ..utils.admin import login_user
from ..utils.commons import generate_qr_code, verify_otp, get_user_from_session
from django_otp.plugins.otp_totp.models import TOTPDevice


class AdminLoginView(AdminContextMixin, View):
    template_name = "authentication/login.html"

    def get(self, request, *args, **kwargs):
        form = AdminAuthenticationFormWithOTP()
        context = self.get_admin_context()
        context["form"] = form
        context["title"] = "Login"
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = AdminAuthenticationFormWithOTP(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                request.session["pre_2fa_user_id"] = user.id
                if user.is_staff and not (user.is_superuser or user.role in User.SUPERUSER_ROLES):
                    return login_user(request, user)
                elif not (
                    user.is_staff
                    and (user.role in User.SUPERUSER_ROLES or user.is_superuser)
                ):
                    form.add_error(None, "You must be admin to proceed.")
                elif not user.is_two_factor_enabled:
                    return redirect("admin-generate-qr_code")
                else:
                    return redirect("admin-verify-otp")
            else:
                form.add_error(None, "Invalid username or password")

        context = self.get_admin_context()
        context["form"] = form
        return render(request, self.template_name, context)


class AdminVerifyOTPView(AdminContextMixin, View):
    template_name = "authentication/verify_otp.html"

    def get_totp_device(self, user):
        try:
            return TOTPDevice.objects.filter(user=user).first()
        except Exception as e:
            return redirect("admin-generate-qr_code")

    def get(self, request, *args, **kwargs):
        user = get_user_from_session(request)

        if not user:
            return redirect("admin-login")

        device = self.get_totp_device(user)
        form = OTPVerificationForm(digits=device.digits)
        context = self.get_admin_context()
        context["form"] = form
        context["title"] = "Verify OTP"
        context["digits"] = device.digits

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = get_user_from_session(request)
        if not user:
            return redirect("admin-login")

        device = self.get_totp_device(user)
        form = OTPVerificationForm(request.POST, digits=device.digits)

        if form.is_valid():
            otp_token = form.cleaned_data.get("otp_token")
            success, message = verify_otp(user, otp_token)
            if success:
                return login_user(request, user)
            else:
                form.add_error("otp_token", message)

        context = self.get_admin_context()
        context["form"] = form
        context["digits"] = device.digits
        return render(request, self.template_name, context)


class AdminGenerateQRCodeView(AdminContextMixin, View):
    template_name = "authentication/generate_qr_code.html"

    def get(self, request, *args, **kwargs):
        user = get_user_from_session(request)
        if not user:
            return redirect("admin-login")

        try:
            qr_code_base64 = generate_qr_code(user)
            context = self.get_admin_context()
            context["qr_code_base64"] = qr_code_base64
            return render(request, self.template_name, context)
        except Exception as e:
            return redirect("admin-login")

    def post(self, request, *args, **kwargs):
        return redirect("admin-verify-otp")
