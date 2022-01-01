from string import Template
from django import forms
from django.http import HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import render,get_object_or_404
from django.urls.base import reverse_lazy
from django.views.generic import CreateView,FormView,TemplateView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F
from django.views.generic.detail import DetailView
from .models import Slot,Shift,User,ShiftTemplate,Block
from .forms import ShiftForm, ShiftFormFromTemplate
from datetime import timedelta
import pandas as pd
import numpy as np
from ortoolpy.etc import addvar
from pulp import *
from ortoolpy import addvars, addbinvars
from django_pandas.io import read_frame 
# Create your views here.
#回答フォームのビュー
def shift_recruit_view(request,pk):
    shift=get_object_or_404(Shift, pk=pk)
    forms=ShiftForm(request.POST or None, instance=shift)
    if forms.is_valid():
        forms.save()
    return render(request,'shift_maker/answer.html',{'forms':forms,'shift':shift})
#回答処理用の関数
def shift_receive_answer_view(request,pk):
    user=request.user
    answer=request.POST.getlist('slot')
    testslots=user.assigning_slot.all()
    for answer_slot_id in answer:
        slot=Slot.objects.get(id=answer_slot_id)
        user.assigning_slot.add(slot)
        user.save()
    for slot in testslots:
        print(slot.workname)
    return HttpResponseRedirect(reverse('shift_maker:mypage'))

class RecruitDetailView(DetailView):
    model=Shift
    template_name="shift_maker/recruit_detail.html"

class CreateSlotView(CreateView):
    model=Slot
    fields="__all__"

class CreateShiftTemplate(CreateView):
    model=ShiftTemplate
    fields="__all__"

class CreateShift(CreateView):
    model=Shift

class ShiftFormFromTemplateView(FormView):
    template_name='shift_maker/templateconvert.html'
    form_class=ShiftFormFromTemplate
    success_url=reverse_lazy("shift_maker:mypage")

class MyPageView(LoginRequiredMixin,TemplateView):
    model=User
    template_name="shift_maker/mypage.html"
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['decided_assign_slot']=self.request.user.assigning_slot.filter(is_decided=True)
        context['undecided_assign_slot']=self.request.user.assigning_slot.filter(is_decided=False)
        context['lack_slot']=Slot.objects.annotate(assigning_number=Count('slot_users')).filter(assigning_number__lt=F('required_number'),is_decided=True)
        context['shifts']=Shift.objects.all
        context['made_shifts']=Shift.objects.filter(creater=self.request.user)
        return context    
#シフトのテンプレートからShiftModelを作る関数
#TODO 不正なフォームへの対応
def shift_from_template(request):
    form=ShiftFormFromTemplate(data=request.POST)
    if request.method=="POST":
        if form.is_valid():
            selected_shift_template=form.cleaned_data.get('shift_template')
            slots=selected_shift_template.slot_templates.all()
            first_day=form.cleaned_data.get('first_day')
            print(first_day)
            shift_name=form.cleaned_data.get('shift_name')
            deadline=form.cleaned_data.get('deadline')
            target=form.cleaned_data.get('target')
            creater=request.user
            shift=Shift.objects.create(shift_name=shift_name,first_day=first_day,deadline=deadline,target=target,creater=creater)
            for slot in slots:
                slot.day=first_day+timedelta(days=slot.days_from_start)
                slot.id=None
                slot.save()
                shift.slot.add(slot)
            return HttpResponseRedirect(reverse('shift_maker:mypage'))
        elif request.method=="GET":
            print("Get")
            return HttpResponseRedirect(reverse('shift_maker:shift_create_form_template'))
        else:
            for i in form:
                print(i)
            return HttpResponseRedirect(reverse('shift_maker:shift_create_form_template'))
    else:
        print("NOt Post")
        return HttpResponseRedirect(reverse('shift_maker:shift_create_form_template'))

def shift_calculate(request,pk):
    shift=get_object_or_404(Shift,pk=pk)
    #モデルインスタンスのフィールドの値をvalues_list で取り出してそれをlist()でlist化して
    #Pandasの列又は行に追加している
    #values_list で値を取り出した際の順序がどのようになっているのかわかっていないので順序が
    #おかしくなっている可能性あり
    slots=shift.slot.all()
    slot_df=read_frame(slots,fieldnames=["required_number","content__workload","content__id"],index_col="id")
    users=User.objects.filter(Block_name=shift.target)
    users_df=read_frame(users,fieldnames=["workload_sum"],index_col="id")
    user_ids=users.values_list("id",flat=True)
    user_list=list(user_ids)
    df=pd.DataFrame(index=slot_df.index,columns=user_list)
    df.fillna(0,inplace=True)    
    workcontents=[]
    for slot in slots:
        workcontents.append(slot.content.id)
        assigning_workers=slot.slot_users.all()
        for assigning_worker in assigning_workers:
            df.at[slot.id,assigning_worker.id]=1
    list(set(workcontents))
    exp_df=pd.DataFrame(index=workcontents,columns=user_list)
    exp_df.fillna(0,inplace=True)
    #経験済みの仕事を列挙している    
    for user_id in user_list:
        usermodel=User.objects.get(id=user_id)
        assigned_works=usermodel.assigned_work.all()
        for assigned_work in assigned_works:
            index=assigned_work.id
            if index in workcontents:
                exp_df.at[index,user_id]=1
    #時間帯が重複しているシフト枠の組を取り出す処理。日付ごとに行っている
    days=slots.values_list("days_from_start",flat=True)
    days_list=list(set(days))
    overlapping_pairs=[]
    for day in days_list:
        day_slots=slots.filter(days_from_start=day)
        for day_slot in day_slots:
            day_slots=day_slots.exclude(id=day_slot.id)
            for other_slot in day_slots:
                if other_slot.start_time < day_slot.end_time and other_slot.end_time >day_slot.start_time:
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
    #エラー発生中
    print(overlapping_pairs)
    print()
    for index,r in var.iteritems():
        for i in range(len(overlapping_pairs)):
            k+=r[overlapping_pairs[i][0]]+r[overlapping_pairs[i][1]]<=1
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
        k+=lpDot(slot_df["content__workload"],w) + users_df.at[column,"workload_sum"]<=V_worksum_diff
    #コストを計算
    k+=C_need_diff_over*lpSum(df.V_need_dif_over)\
    +C_need_diff_shortage*lpSum(df.V_need_dif_shortage)\
    +C_experience*lpSum(df.V_experience)\
    +C_minmax*V_worksum_diff
    k.solve()
    print(var)
    result_np= np.vectorize(value)(var).astype(int)
    result=pd.DataFrame(result_np,index=slot_df.index,columns=user_list)
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
    Slot.objects.bulk_update(slots,["is_decided"])
    return HttpResponseRedirect(reverse('shift_maker:mypage'))

    
# 人数不足スロットの表示・登録処理　
class LackSlotDetailView(DetailView):
    model=Slot
    template_name="shift_maker/lack_slot_detail.html"

def assign_lack_slot(request,pk):
    slot=Slot.objects.get(pk=pk)
    user=request.user
    workload=Slot.objects.values_list("content__workload",flat=True).get(pk=pk)
    user.assigning_slot.add(slot)
    user.workload_sum+=workload
    user.save()
    return HttpResponseRedirect(reverse('shift_maker:mypage'))

class AssigningSlotDetailView(DetailView):
    model=Slot
    template_name="shift_maker/decided_slot_detail.html"

# 登録済みスロットの登録解除
def delete_assigned_slot(request,pk):
    slot=Slot.objects.get(pk=pk)
    user=request.user
    workload=Slot.objects.values_list("content__workload",flat=True).get(pk=pk)
    user.assigning_slot.remove(slot)
    user.workload_sum-=workload
    user.save()
    return HttpResponseRedirect(reverse('shift_maker:mypage'))

# 予約済みスロットの予約解除
class BookingSlotDetailView(DetailView):
    model=Slot
    template_name="shift_maker/booking_slot_detail.html"

def delete_booking_slot(request,pk):
    slot=Slot.objects.get(pk=pk)
    user=request.user
    user.assigning_slot.remove(slot)
    user.save()
    return HttpResponseRedirect(reverse('shift_maker:mypage'))

    