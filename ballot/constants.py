from django.utils.translation import gettext as _


POLL_TYPE_BY_SHARE = 1
POLL_TYPE_BY_LOT = 2

POLL_TYPES = (
    (POLL_TYPE_BY_SHARE, _('By Share')),
    (POLL_TYPE_BY_LOT, _('By Lot')),
)
