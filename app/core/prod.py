# from .base import *

import ldap
from django_auth_ldap.config import (
    LDAPSearch,
    LDAPSearchUnion,
    ActiveDirectoryGroupType,
)

# LDAP authentification
AUTH_LDAP_SERVER_URI = "ldap://192.168.40.2"
AUTH_LDAP_BIND_DN = "CN=eye_link,OU=Users,OU=UTILISATEURS_PACCI,DC=pac-ci,DC=org"
AUTH_LDAP_BIND_PASSWORD = "@---Kondj^é59as36..45"

AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(
    LDAPSearch(
        "OU=Users,OU=UTILISATEURS_PACCI,DC=pac-ci,DC=org",
        ldap.SCOPE_SUBTREE,
        "sAMAccountName=%(user)s",
    ),
    LDAPSearch(
        "OU=Admins,OU=UTILISATEURS_PACCI,DC=pac-ci,DC=org",
        ldap.SCOPE_SUBTREE,
        "sAMAccountName=%(user)s",
    ),
    LDAPSearch(
        "OU=Powers_users,OU=UTILISATEURS_PACCI,DC=pac-ci,DC=org",
        ldap.SCOPE_SUBTREE,
        "sAMAccountName=%(user)s",
    ),
)

AUTH_LDAP_USER_ATTR_MAP = {
    "username": "sAMAccountName",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "dc=pac-ci,dc=org", ldap.SCOPE_SUBTREE, "(objectCategory=Group)"
)
AUTH_LDAP_GROUP_TYPE = ActiveDirectoryGroupType(name_attr="cn")
# AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#     "is_superuser": "CN=django_admins,OU=GROUPE_PACCI,DC=pac-ci,DC=org",
#     "is_staff": "CN=django_admins,OU=GROUPE_PACCI,DC=pac-ci,DC=org",
# }
# AUTH_LDAP_FIND_GROUP_PERMS = True
# AUTH_LDAP_CACHE_GROUPS = True
# AUTH_LDAP_GROUP_CACHE_TIMEOUT = 1  # 1 hour cache

AUTHENTICATION_BACKENDS = (
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"django_auth_ldap": {"level": "DEBUG", "handlers": ["console"]}},
}
