from django import forms
from .models import Shift, ShiftTemplate, Block

class ShiftForm(forms.ModelForm):
    class Meta():
        model=Shift
        fields=('slot')
#シフト表のテンプレートからシフト表を作るフォーム           
class ShiftFormFromTemplate(forms.Form):
    shift_template=forms.ModelChoiceField(queryset=ShiftTemplate.objects.all())
    first_day=forms.DateField()
    shift_name=forms.CharField(max_length=40　verbose_name="シフト名")
    deadline=forms.DateField()
    target=forms.CharField(max_length=Block.MAX_LENGTH,choices=Block.choices)

