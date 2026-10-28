from decimal import Decimal

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Sum

from .models import Expense, Member, Trip


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)


class TripForm(forms.ModelForm):
    budget = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0"),
        required=False,
        help_text="Optional",
    )

    class Meta:
        model = Trip
        fields = ("name", "budget")

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Enter a trip name.")
        return name

    def save(self, commit=True):
        trip = super().save(commit=False)
        trip.budget = float(self.cleaned_data.get("budget") or 0)
        if commit:
            trip.save()
        return trip


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ("name", "mobile")

    def __init__(self, *args, trip, **kwargs):
        self.trip = trip
        super().__init__(*args, **kwargs)
        self.fields["mobile"].required = False

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if Member.objects.filter(trip=self.trip, name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This member is already in the trip.")
        return name


class ExpenseForm(forms.ModelForm):
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )
    participants = forms.ModelMultipleChoiceField(
        queryset=Member.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Leave all unchecked to split equally with everyone.",
    )

    class Meta:
        model = Expense
        fields = ("name", "amount", "paid_by", "participants", "category", "description")

    def __init__(self, *args, trip, **kwargs):
        self.trip = trip
        super().__init__(*args, **kwargs)
        members = trip.members.order_by("id")
        self.fields["paid_by"].queryset = members
        self.fields["participants"].queryset = members
        self.fields["category"].required = False
        self.fields["description"].required = False

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Enter an expense name.")
        return name

    def clean_category(self):
        return self.cleaned_data.get("category") or "Other"

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get("amount")
        if amount is not None and self.trip.budget > 0:
            spent = self.trip.expenses.aggregate(total=Sum("amount"))["total"] or 0
            spent_amount = Decimal(str(spent)).quantize(Decimal("0.01"))
            budget = Decimal(str(self.trip.budget)).quantize(Decimal("0.01"))
            if spent_amount + amount > budget:
                self.add_error("amount", "This expense would exceed the trip budget.")
        return cleaned_data
