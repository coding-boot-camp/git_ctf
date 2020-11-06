from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from drf_yasg.openapi import IN_QUERY, TYPE_STRING, Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_auth.registration.views import RegisterView as BaseRegisterView
from rest_auth.registration.views import SocialConnectView, SocialLoginView
from rest_framework.exceptions import NotFound, ValidationError, bad_request
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.models import Profile
from core.permissions import HasGroupPermission
from core.serializers import (
    CustomSocialLoginSerializer,
    ProfileSerializer,
    UserSerializer,
)

sensitive_param = method_decorator(
    sensitive_post_parameters("password"), name="dispatch"
)

email_param = Parameter(
    "email",
    IN_QUERY,
    "Email belonging to the Profile's User instance",
    required=True,
    type=TYPE_STRING,
)


class UpdateProfile(RetrieveUpdateAPIView):
    """
    API View for retrieving and updating the logged in user's profile info like
    military service details, current employment, etc
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """
        Overrides `get_object` to pull the user profile
        off the current authenticated user
        """
        obj = self.request.user.profile
        self.check_object_permissions(self.request, obj)
        return obj


class AdminUpdateProfile(RetrieveUpdateAPIView):
    """
    Read or update user profiles
    """

    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = (HasGroupPermission,)
    required_groups = {
        "GET": ["ProfileAdmin"],
        "PUT": ["ProfileAdmin"],
        "PATCH": ["ProfileAdmin"],
    }

    def get_object(self):
        email = self.request.query_params.get("email")
        if email:
            try:
                profile = Profile.objects.get(user__email=email)
            except Profile.DoesNotExist:
                raise NotFound

            self.check_permissions(self.request)
            return profile

        raise ValidationError({"error": "Missing email query param"})

    @swagger_auto_schema(manual_parameters=[email_param])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[email_param])
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[email_param])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)


class UserView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """
        Overrides `get_object` to pull the user
        off the current authenticated session
        """
        obj = self.request.user
        self.check_object_permissions(self.request, obj)
        return obj


@sensitive_param
class RegisterView(BaseRegisterView):
    pass


class GoogleLogin(SocialLoginView):
    permission_classes = (AllowAny,)
    adapter_class = GoogleOAuth2Adapter
    serializer_class = CustomSocialLoginSerializer


class GoogleConnect(SocialConnectView):
    adapter_class = GoogleOAuth2Adapter


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    serializer_class = CustomSocialLoginSerializer


class FacebookConnect(SocialConnectView):
    adapter_class = FacebookOAuth2Adapter


class GithubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = settings.GITHUB_AUTH_CALLBACK_URL
    client_class = OAuth2Client


class GithubConnect(SocialConnectView):
    adapter_class = GitHubOAuth2Adapter
