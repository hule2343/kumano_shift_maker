from django import forms
from .models import Shift, ShiftTemplate, Block

#シフト回答フォーム
class ShiftForm(forms.ModelForm):
    class Meta():
        model=Shift
        fields=('slot',)
#シフト表のテンプレートからシフト表を作るフォーム           
class ShiftFormFromTemplate(forms.Form):
    shift_template=forms.ModelChoiceField(queryset=ShiftTemplate.objects.all())
    first_day=forms.DateField(label="シフト初日の日付",widget=forms.DateInput(attrs={"type":"date"}))
    shift_name=forms.CharField(max_length=40,label="シフト名")
    deadline=forms.DateField(label="シフト募集締切日",widget=forms.DateInput(attrs={"type":"date"}))
    target=forms.ChoiceField(required=True,choices=Block.choices,label="対象ブロック")

