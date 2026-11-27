import re

from django import forms

from .models import Device


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ("device_name", "device_type", "mac_address")
        widgets = {
            "device_name": forms.TextInput(attrs={"placeholder": "e.g. Living Room Laptop"}),
            "device_type": forms.TextInput(attrs={"placeholder": "e.g. Laptop, Phone, Smart TV"}),
            "mac_address": forms.TextInput(attrs={"placeholder": "AA:BB:CC:DD:EE:FF"}),
        }

    def clean_mac_address(self):
        value = self.cleaned_data["mac_address"].strip().upper().replace("-", ":")
        if not re.fullmatch(r"(?:[0-9A-F]{2}:){5}[0-9A-F]{2}", value):
            raise forms.ValidationError("Enter a valid MAC address (for example, AA:BB:CC:DD:EE:FF).")
        return value
