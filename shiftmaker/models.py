from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class WorkContent(models.Model):
    contentname=models.CharField(max_length=25)
    workload=models.IntegerField()
    

class Slot(models.Model):
    workname=models.CharField(max_length=30,null=True,blank=True)
    day=models.DateField(blank=True)
    start_time=models.TimeField(blank=True)
    end_time=models.TimeField(blank=True)
    days_from_start=models.PositiveIntegerField(blank=True) #1日目は０
    required_number=models.PositiveIntegerField()
    content=models.ForeignKey(WorkContent,on_delete=models.SET_DEFAULT,default='無し')
    is_decided=models.BooleanField(default=False)#既に募集締め切りが過ぎた枠かどうか
    
class Block(models.TextChoices):
    a1='a1','A1'
    a2='a2','A2'
    a3='a3','A3'
    a4='a4','A4'
    b12='b12','B12'
    b3='b3','B3'
    b4='b4','B4'
    c12='c12','C12'
    c34='c34','C34'
    all='all','All'

class User(AbstractBaseUser):
    Block_name=models.CharField(max_length=Block.MAX_LENGTH,choices=Block.choices)
    room_number=models.Integer()
    account_name=models.CharField(max_length=40,verbose_name='アカウント名')
    workload_sum=models.IntegerField(verbose_name='過去の仕事量')
    assigned_work=models.ManyToManyField(WorkContent,verbose_name='経験済みの仕事')
    assigning_slot=models.ManyToManyField(Slot)
    password=models.CharField(max_length=128, verbose_name='password')
    objects=MyUserManager()
    USERNAME_FIELD='account_name'


class Shift(models.Model):
    shift_name=models.CharField(max_length=40,verbose_name="シフト名")
    first_day=models.DateField()
    deadline=models.DateField()
    slot=models.ManyToManyField(Slot)
    target=models.CharField(max_length=Block.MAX_LENGTH,choices=Block.choices)

class ShiftTemplate(models.Model):
    shift_template_name=models.CharField(max_length=40,verbose_name="テンプレート名")
    slot_templates=models.ManyToManyField(Slot)
