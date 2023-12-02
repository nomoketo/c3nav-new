from collections import namedtuple
from dataclasses import dataclass
from enum import StrEnum
from importlib import import_module

from django.contrib.auth import get_user as auth_get_user
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.utils import timezone
from django.utils.functional import SimpleLazyObject, lazy
from ninja.security import HttpBearer

from c3nav import settings
from c3nav.api.exceptions import APIPermissionDenied, APITokenInvalid
from c3nav.api.models import Secret
from c3nav.api.schema import APIErrorSchema
from c3nav.control.middleware import UserPermissionsMiddleware
from c3nav.control.models import UserPermissions

FakeRequest = namedtuple('FakeRequest', ('session', ))


class APIAuthMethod(StrEnum):
    ANONYMOUS = 'anonymous'
    SESSION = 'session'
    SECRET = 'secret'


@dataclass
class NewAPIAuth:
    method: APIAuthMethod
    readonly: bool


description = """
An API token can be acquired in 4 ways:

* Use `anonymous` for guest access.
* Generate a session-bound temporary token using the auth session endpoint.
* Create an API secret in your user account settings.
""".strip()


class APITokenAuth(HttpBearer):
    openapi_name = "api token authentication"
    openapi_description = description

    def __init__(self, logged_in=False, superuser=False, permissions: set[str] = None, is_readonly=False):
        super().__init__()
        self.logged_in = superuser or logged_in
        self.superuser = superuser
        self.permissions = permissions or set()
        self.is_readonly = is_readonly
        engine = import_module(settings.SESSION_ENGINE)
        self.SessionStore = engine.SessionStore

    def _authenticate(self, request, token) -> NewAPIAuth:
        request.user = AnonymousUser()
        request.user_permissions = SimpleLazyObject(lambda: UserPermissionsMiddleware.get_user_permissions(request))
        request.user_space_accesses = lazy(UserPermissionsMiddleware.get_user_space_accesses, dict)(request)

        if token == "anonymous":
            return NewAPIAuth(
                method=APIAuthMethod.ANONYMOUS,
                readonly=True,
            )
        elif token.startswith("session:"):
            session = self.SessionStore(token.removeprefix("session:"))
            print('session is empty:', request.session.is_empty())
            user = auth_get_user(FakeRequest(session=session))
            if not user.is_authenticated:
                raise APITokenInvalid
            request.user = user
            return NewAPIAuth(
                method=APIAuthMethod.SESSION,
                readonly=True,
            )
        elif token.startswith("secret:"):
            try:
                secret = Secret.objects.filter(
                    Q(api_secret=token.removeprefix("secret:")),
                    Q(valid_until__isnull=True) | Q(valid_until__lt=timezone.now()),
                ).select_related("user", "user__permissions").get()
            except Secret.DoesNotExist:
                raise APITokenInvalid

            # get user permissions and restrict them based on scopes
            user_permissions: UserPermissions = secret.user.permissions
            if secret.scope_mesh is False:
                user_permissions.mesh_control = False
            if secret.scope_editor is False:
                user_permissions.editor_access = False
            if secret.scope_grant_permissions is False:
                user_permissions.grant_permissions = False

            request.user = secret.user
            request.user_permissions = user_permissions

            return NewAPIAuth(
                method=APIAuthMethod.SESSION,
                readonly=secret.readonly
            )
        raise APITokenInvalid

    def authenticate(self, request, token):
        auth_result = self._authenticate(request, token)
        if self.logged_in and not request.user.is_authenticated:
            raise APIPermissionDenied('You need to be signed in for this request.')
        if self.superuser and not request.user.is_superuser:
            raise APIPermissionDenied('You need to have admin rights for this endpoint.')
        for permission in self.permissions:
            if not getattr(request.user_permissions, permission):
                raise APIPermissionDenied('You need to have the "%s" permission for this endpoint.')
        if request.method == 'GET' and self.is_readonly:
            raise ValueError('this makes no sense for GET')
        if request.method != 'GET' and not self.is_readonly and auth_result.readonly:
            raise APIPermissionDenied('You need a non-readonly API access key for this endpoint.')
        return auth_result


validate_responses = {422: APIErrorSchema, }
auth_responses = {401: APIErrorSchema, }
auth_permission_responses = {401: APIErrorSchema, 403: APIErrorSchema, }
