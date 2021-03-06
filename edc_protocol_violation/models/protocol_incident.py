from edc_action_item.managers import (
    ActionIdentifierManager,
    ActionIdentifierSiteManager,
)
from edc_action_item.models import ActionModelMixin
from edc_identifier.model_mixins import (
    NonUniqueSubjectIdentifierFieldMixin,
    TrackingModelMixin,
)
from edc_model.models import BaseUuidModel
from edc_sites.models import SiteModelMixin

from ..constants import PROTOCOL_INCIDENT_ACTION
from ..model_mixins import ProtocolIncidentModelMixin


class ProtocolIncident(
    ProtocolIncidentModelMixin,
    NonUniqueSubjectIdentifierFieldMixin,
    SiteModelMixin,
    ActionModelMixin,
    TrackingModelMixin,
    BaseUuidModel,
):
    action_name = PROTOCOL_INCIDENT_ACTION
    tracking_identifier_prefix = "PD"
    on_site = ActionIdentifierSiteManager()
    objects = ActionIdentifierManager()

    def natural_key(self):
        return (self.action_identifier,)  # noqa

    class Meta(ProtocolIncidentModelMixin.Meta, BaseUuidModel.Meta):
        pass
