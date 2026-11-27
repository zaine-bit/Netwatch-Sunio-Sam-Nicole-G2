import re

from django import forms
from django.utils import timezone

from .models import Device, UsageLog


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


class UsageLogForm(forms.ModelForm):
    class Meta:
        model = UsageLog
        fields = ("usage_date", "data_used_mb")
        labels = {
            "usage_date": "Usage date",
            "data_used_mb": "Data used (MB)",
        }
        widgets = {
            "usage_date": forms.DateInput(attrs={"type": "date"}),
            "data_used_mb": forms.NumberInput(attrs={"min": "0", "step": "0.01", "placeholder": "e.g. 125.50"}),
        }

    def clean_usage_date(self):
        usage_date = self.cleaned_data["usage_date"]
        if usage_date > timezone.localdate():
            raise forms.ValidationError("Usage date cannot be in the future.")
        return usage_date

    def clean_data_used_mb(self):
        amount = self.cleaned_data["data_used_mb"]
        if amount < 0:
            raise forms.ValidationError("Data usage cannot be negative.")
        return amount
