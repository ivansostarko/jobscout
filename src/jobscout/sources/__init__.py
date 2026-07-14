"""Job sources registry."""
from __future__ import annotations

from .linkedin import LinkedInSource
from .mojposao import MojPosaoSource
from .posao_hr import PosaoHrSource
from .burza_hzz import BurzaHzzSource
from .facebook_groups import FacebookGroupsSource

SOURCES = {
    "linkedin": LinkedInSource,
    "mojposao": MojPosaoSource,
    "posao_hr": PosaoHrSource,
    "burza_hzz": BurzaHzzSource,
    "facebook_groups": FacebookGroupsSource,
}
