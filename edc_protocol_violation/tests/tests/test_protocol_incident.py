from copy import deepcopy
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django.test.testcases import TestCase
from edc_action_item import site_action_items
from edc_constants.constants import CLOSED, NO, NOT_APPLICABLE, OPEN, OTHER
from edc_list_data import site_list_data
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow

from edc_protocol_violation import list_data
from edc_protocol_violation.constants import DEVIATION
from edc_protocol_violation.forms import ProtocolIncidentForm
from edc_protocol_violation.models import (
    ActionsRequired,
    ProtocolIncident,
    ProtocolViolations,
)

from ..action_items import ProtocolIncidentAction
from ..models import TestModel  # noqa


class TestProtocolIncident(TestCase):
    def setUp(self):
        site_action_items.registry = {}
        action_cls = ProtocolIncidentAction
        site_action_items.register(action_cls)
        site_list_data.initialize()
        site_list_data.register(list_data, app_name="edc_protocol_violation")
        site_list_data.load_data()

        self.subject_identifier = "1234"
        RegisteredSubject.objects.create(subject_identifier=self.subject_identifier)

        action = ProtocolIncidentAction(subject_identifier=self.subject_identifier)
        self.data = dict(
            tracking_identifier=uuid4().hex,
            action_identifier=action.action_item.action_identifier,
        )

    def test_incident_open_ok(self):
        data = deepcopy(self.data)
        data.update(
            {
                "subject_identifier": self.subject_identifier,
                "report_datetime": get_utcnow(),
                "report_status": OPEN,
                "report_type": DEVIATION,
                "safety_impact": NOT_APPLICABLE,
                "short_description": "sdasd asd asdasd ",
                "study_outcomes_impact": NOT_APPLICABLE,
            }
        )
        obj = ProtocolIncident(**data)
        obj.save()

    def test_incident_open_form(self):
        data = deepcopy(self.data)
        data.update(
            {
                "report_datetime": get_utcnow(),
                "report_status": OPEN,
                "report_type": DEVIATION,
                "safety_impact": NO,
                "short_description": "sdasd asd asdasd ",
                "study_outcomes_impact": NO,
                "incident_datetime": get_utcnow() - relativedelta(days=3),
                "incident": ProtocolViolations.objects.get(name=OTHER),
                "incident_other": "blah blah",
                "incident_description": "blah blah",
                "incident_reason": "blah blah",
                "violation": None,
            }
        )

        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_incident_try_to_close_form(self):
        data = deepcopy(self.data)
        data.update(
            {
                "report_datetime": get_utcnow() - relativedelta(days=1),
                "report_status": OPEN,
                "report_type": DEVIATION,
                "safety_impact": NO,
                "short_description": "sdasd asd asdasd ",
                "study_outcomes_impact": NO,
                "incident_datetime": get_utcnow() - relativedelta(days=3),
                "incident": ProtocolViolations.objects.get(name=OTHER),
                "incident_other": "blah blah",
                "incident_description": "blah blah",
                "incident_reason": "blah blah",
                "violation": None,
            }
        )

        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        # self.assertIn("corrective_action_datetime", form._errors)
        data.update(corrective_action_datetime=get_utcnow())
        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        self.assertIn("corrective_action", form._errors)

        data.update(corrective_action="we took corrective action")
        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        # self.assertIn("preventative_action_datetime", form._errors)

        data.update(preventative_action_datetime=get_utcnow())
        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        self.assertIn("preventative_action", form._errors)

        data.update(preventative_action="we took preventative action", report_status=CLOSED)
        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        self.assertIn("action_required", form._errors)

        data.update(action_required=ActionsRequired.objects.get(name="remain_on_study"))
        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        self.assertIn("report_closed_datetime", form._errors)

        data.update(report_closed_datetime=get_utcnow())
        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        self.assertEqual({}, form._errors)
