from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse
from .models import Slot,Shift,User
import pandas as pd
import numpy as np
from ortoolpy.etc import addvar
from pulp import *
from ortoolpy import addvars, addbinvars
# Create your views here.
#回答フォームの作成ビュー
def shift_recruit_view(request,pk):
    shift=get_object_or_404(Shift, pk=pk)
    form=forms.ShiftForm(request.POST or None, instance=shift)
    if form.is_valid():
        form.save()
    return render(request,'shift_maker/answer.html',{'form':form})
#回答処理用の関数
def shift_receive_answer_view(request,pk):
    user=request.user
    answer=request.POST.getlist('slot')
    for answer_slot_id in answer:
        slot=Slot.objects.get(id=answer_slot_id)
        user.assigning_slot.add(slot)
        user.save()
    return HttpResponseRedirect(reverse('shift_maker:mypage', args=(user.id,)))

class CreateSlotView(CreateView):
    model=Slot
    fields=__all__

class CreateShiftTemplate(CreateView):
    model=ShiftTemplate
    fields=__all__

class CreateShift(CreateView):
    model=Shift

class ShiftFormFromTemplateView(FormView):
    template_name='shift_maker/templateconvert.html'
    form_class=ShiftFormFromTemplate
    success_url=reverse('shift_maker:shift_from_template')
#シフトのテンプレートからShiftModelを作る関数
#TODO 不正なフォームへの対応
def shift_from_template(request):
    form=forms.ShiftFormFromTemplate(request.POST)
    selected_shift_template=form.cleaned_data.get('shift_template')
    slots=selected_shift_template.slot_templates.all()
    first_day=form.cleaned_data.get('first_day')
    shift_name=form.cleaned_data.get('shift_name')
    deadline=form.cleaned_data.get('deadline')
    target=form.cleaned_data_.get('target')
    for slot in slots:
        slot.day=first_day+datetime.timedelta(days=slot.days_from_start)
    Shift.objects.create(shift_name=shift_name,first_day=first_day,deadline=deadline,slot=slots,target=target)
    return HttpResponseRedirect(reverse('shift_maker:mypage', args=(request.user.id,)))

def shift_calculate(request,pk):
    shift=get_object_or_404(Shift,pk=pk)
    slots=shift.slot.object.all
    slot_id=slots.values_list("id",flat=True)
    slot_list=list(slot_id)
    user_ids=User.objects.filter(Block_name=shift.target).values_list("id",flat=True)
    user_list=list(user_ids)
    df=pd.DataFrame(index=user_list,colums=slot_list)
    df.fillna(0,inplace=True)
    workcontents=[]
    for slot in slots:
        workcontents.append(slot.content.contentname)
        assigning_workers=slot.user_set.all()
        for assigning_worker in assigning_workers:
            df.at[assigning_worker.id,slot.id]=1
    list(set(workcontents))
    for content in workcontents:
        df[content]=0
    for user_id in user_list:
        usermodel=User.objects.get(id=user_id)
        assigned_works=usermodel.assigned_work.all
        for assigned_work in assigned_works:
            column=assigned_work.contentname
            if column in workcontents:
                df.at[user_id,column]=1
    #時間帯が重複しているシフト枠の組を取り出す処理。日付ごとに行っている
    days=slots.values_list("days_from_start",flat=True)
    days_list=list(set(days))
    overlapping_pairs=[]
    for day in days_list:
        day_slots=slot.filter(days_from_start=day)
        for day_slot in day_slots:
            day_slots=day_slots.exclude(id=day_slot.id)
            for other_slot in day_slots:
                if other_slot.start_time < day_slot.end_time and other_slot.endtime >day_slot.start_time:
                    overlapping_pair=[day_slot.id,other_slot.id]
                    overlapping_pairs.append(overlapping_pair)

    var = pd.DataFrame(np.array(addbinvars(len(user_list), len(slot_list))),index=user_list, columns=slot_list)
    shift_rev = df[df.columns].apply(lambda r: 1-r[df.columns],1)
    k=LpProblem()
    #希望していない枠に入らないようにする制約条件
    for (_, h),(_, n) in zip(shift_rev.iterrows(),var.iterrows()):
        k += lpDot(h, n) <= 0
    #同じ時間帯の枠に同じ人が入らないようにする制約条件    
    for pair in overlapping_pairs:
        k+=lpDot(var.pair[0],var.pair[1])<=0

    df.loc['V_need_dif_over']=addvars(len(slot_list))
    df.loc['V_need_dif_shortage']=addvars(len(slot_list))
    df.loc['V_experience']=addvars(len(slot_list))
    for (_, r),(column, d) in zip(df.iteritems(),var.iteritems()):
        slot_need=slots.objects.get(id=column).required_number
        k += r.V_need_dif_over >= (lpSum(d) - slot_need)
        k += r.V_need_dif_shortage >= -(lpSum(d) - slot_need)

#TODO 人数不足スロットの表示・登録処理　
#TODO 登録済みスロットの登録解除
#TODO 予約済みスロットの予約解除