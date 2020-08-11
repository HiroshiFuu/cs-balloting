from django.utils.translation import gettext as _


USER_TYPE_GUEST = 1
USER_TYPE_USER = 2
USER_TYPE_COMPANY = 3
USER_TYPE_ADMIN = 4
USER_TYPE_SYSADMIN = 5

USER_TYPES = (
    (USER_TYPE_GUEST, _('Guest')),
    (USER_TYPE_USER, _('User')),
    (USER_TYPE_COMPANY, _('Company')),
    (USER_TYPE_ADMIN, _('Admin')),
    (USER_TYPE_SYSADMIN, _('SysAdmin')),
)
