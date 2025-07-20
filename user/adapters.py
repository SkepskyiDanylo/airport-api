from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = sociallogin.user
        user.email = user_email(user)
        user.set_unusable_password()
        user.password_login_enabled = False
        user.save()
        sociallogin.save(request)
        return user
