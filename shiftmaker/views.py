from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render,get_object_or_404
from django.views.generic import CreateView,FormView
from django.urls import reverse
from .models import Slot,Shift,User,ShiftTemplate
from .forms import ShiftFormFromTemplate
from datetime import timedelta
import pandas as pd
import numpy as np
from ortoolpy.etc import addvar
from pulp import *
from ortoolpy import addvars, addbinvars
from django_pandas.io import read_frame 
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
        slot.day=first_day+timedelta(days=slot.days_from_start)
    Shift.objects.create(shift_name=shift_name,first_day=first_day,deadline=deadline,slot=slots,target=target)
    return HttpResponseRedirect(reverse('shift_maker:mypage', args=(request.user.id,)))

def shift_calculate(request,pk):
    shift=get_object_or_404(Shift,pk=pk)
    #モデルインスタンスのフィールドの値をvalues_list で取り出してそれをlist()でlist化して
    #Pandasの列又は行に追加している
    #values_list で値を取り出した際の順序がどのようになっているのかわかっていないので順序が
    #おかしくなっている可能性あり
    slots=shift.slot.object.all
    slot_df=read_frame(slots,fieldnames=["required_number","content__workload","content__id"],index_col="id")
    users=User.objects.filter(Block_name=shift.target)
    users_df=read_frame(users,fieldnames=["workload_sum"],index_col="id")
    user_ids=users.values_list("id",flat=True)
    user_list=list(user_ids)
    df=pd.DataFrame(index=slot_df.index,colums=user_list)
    df.fillna(0,inplace=True)    
    workcontents=[]
    for slot in slots:
        workcontents.append(slot.content.id)
        assigning_workers=slot.user_set.all()
        for assigning_worker in assigning_workers:
            df.at[slot.id,assigning_worker.id]=1
    list(set(workcontents))
    exp_df=pd.DataFrame(index=workcontents,columns=user_list).fillna(0,inplace=True)
    #経験済みの仕事を列挙している    
    for user_id in user_list:
        usermodel=User.objects.get(id=user_id)
        assigned_works=usermodel.assigned_work.all
        for assigned_work in assigned_works:
            index=assigned_work.id
            if index in workcontents:
                exp_df.at[index,user_id]=1
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

    var = pd.DataFrame(np.array(addbinvars(len(slot_df.index), len(user_list))),index=slot_df.index, columns=user_list)
    shift_rev = df[df.columns].apply(lambda r: 1-r[df.columns],1)
    k=LpProblem()
    C_need_diff_over=10
    C_need_diff_shortage=1000
    C_experience=10
    C_minmax=10
    #希望していない枠に入らないようにする制約条件
    for (_, h),(_, n) in zip(shift_rev.iterrows(),var.iterrows()):
        k += lpDot(h, n) <= 0
    #同じ時間帯の枠に同じ人が入らないようにする制約条件    
    for index,r in var.iteritems():
        for pair in overlapping_pairs:
            k+=r.pair[0]+r.pair[1]<=1

    df['V_need_dif_over']=addvars(len(slot_df.index))
    df['V_need_dif_shortage']=addvars(len(slot_df.index))
    df['V_experience']=addvars(len(slot_df.index))
    V_worksum_diff=addvar()
    #必要な人数と実際に入る人数の差に対する制約条件
    for (_, r),(index, d) in zip(df.iterrows(),var.iterrows()):
        k += r.V_need_dif_over >= (lpSum(d) - slot_df.at[index,"required_number"])
        k += r.V_need_dif_shortage >= -(lpSum(d) - slot_df.at[index,"required_number"])
    #経験者が少なくとも一人入る制約条件
    for (_, r),(index, d) in zip(df.iterrows(),var.iterrows()):
        k+=lpDot(exp_df.loc[slot_df.at[index,"content__id"]],d)+r.V_experience>=1
    #合計仕事量が均等になるようにする制約条件
    for column,w in var.iteritems():
        k+=lpDot(slot_df["content__load"],w) + users_df.at[column,"workload_sum"]<=V_worksum_diff
    #コストを計算
    k+=C_need_diff_over*lpSum(df.V_need_dif_over)\
    +C_need_diff_shortage*lpSum(df.V_need_dif_shortage)\
    +C_experience*lpSum(df.V_experience)\
    +C_minmax*V_worksum_diff
    k.solve()
    result=pd.DataFrame(np.vectorize(value)(var).astype(int),index=slot_df.index,columns=user_list)
    for column in user_list:
        user=User.objects.get(id=column)
        user.assigning_slot.clear()
        for index in result.index:
            if result.at[index,column]==1:
                slot=Slot.objects.get(id=index)
                user.assigning_slot.add(slot)
                user.workload_sum+=slot_df.at[index,"content__workload"]
                user.save()
    for slot in slots:
        slot.is_decided=True  
    Slot.objects.bulk_update(slots,update_field=["is_decided"])
    
#TODO 人数不足スロットの表示・登録処理　

#TODO 登録済みスロットの登録解除
#TODO 予約済みスロットの予約解除