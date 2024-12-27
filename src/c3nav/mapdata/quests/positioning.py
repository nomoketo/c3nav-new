from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.forms import CharField, HiddenInput
from django.utils.translation import gettext_lazy as _
from shapely import Point
from shapely.geometry import mapping

from c3nav.mapdata.models.geometry.space import RangingBeacon
from c3nav.mapdata.quests.base import ChangeSetModelForm, register_quest, Quest


class RangingBeaconAltitudeQuestForm(ChangeSetModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["altitude"].label = (
            _('How many meters above ground is the access point “%s” mounted?') % self.instance.comment
        )

    def clean_altitude(self):
        data = self.cleaned_data["altitude"]
        if not data:
            raise ValidationError(_("The AP should not be 0m above ground."))
        return data

    class Meta:
        model = RangingBeacon
        fields = ("altitude", )

    def save(self, *args, **kwargs):
        self.instance.altitude_quest = False
        return super().save(*args, **kwargs)

    @property
    def changeset_title(self):
        return f'Altitude Quest: {self.instance.title}'


@register_quest
@dataclass
class RangingBeaconAltitudeQuest(Quest):
    quest_type = "ranging_beacon_altitude"
    quest_type_label = _('Ranging Beacon Altitude')
    quest_type_icon = "router"
    form_class = RangingBeaconAltitudeQuestForm
    obj: RangingBeacon

    @property
    def point(self) -> Point:
        return mapping(self.obj.geometry)

    @classmethod
    def _qs_for_request(cls, request):
        return RangingBeacon.qs_for_request(request).select_related('space',
                                                                    'space__level').filter(altitude_quest=True)


class RangingBeaconBSSIDsQuestForm(ChangeSetModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["look_for_ap"] = CharField(disabled=True, initial=self.instance.import_tag[4:],
                                               widget=HiddenInput())
        self.fields["wifi_bssids"].widget = HiddenInput()

    def clean_bssids(self):
        data = self.cleaned_data["wifi_bssids"]
        if not data:
            raise ValidationError(_("Need at least one bssid."))
        return data

    class Meta:
        model = RangingBeacon
        fields = ("wifi_bssids", )

    @property
    def changeset_title(self):
        return f'Ranging Beacon BSSID Quest: {self.instance.title}'


@register_quest
@dataclass
class RangingBeaconBSSIDsQuest(Quest):
    quest_type = "ranging_beacon_bssids"
    quest_type_label = _('Ranging Beacon Identifier')
    quest_type_icon = "wifi_find"
    form_class = RangingBeaconBSSIDsQuestForm
    obj: RangingBeacon

    @property
    def quest_description(self) -> list[str]:
        return [
            _("This quest only works in the app. It works fully automatically."),
            _("We are trying to find the BSSIDs broadcast by “%s”."),
            _("Please stand near “%s” and wait for the submit button to appear.") % self.obj.title,
            _("This should happen within less than a minute."),
        ]

    @property
    def point(self) -> Point:
        return mapping(self.obj.geometry)

    @classmethod
    def _qs_for_request(cls, request):
        return RangingBeacon.qs_for_request(request).filter(import_tag__startswith="noc:", wifi_bssids=[])
