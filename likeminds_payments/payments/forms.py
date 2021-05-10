from django import forms

plan_choices = (
    ('Monthly Membership', 'Monthly'),
    ('Quarterly Membership', 'Quarterly'),
    ('Half Yearly Membership', 'Half Yearly'),
    ('Yearly Membership', 'Yearly'),
)

class PlanForm(forms.Form):
    community_name = forms.CharField(max_length=128)
    community_id = forms.IntegerField()
    plan_name = forms.ChoiceField(choices=plan_choices)
    plan_cost = forms.FloatField()
    community_join_link = forms.URLField()
    community_manager_mail = forms.CharField(max_length=200)
    community_buddy_mail = forms.CharField(max_length=200)
    