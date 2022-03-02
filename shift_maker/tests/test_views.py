from http.client import ImproperConnectionState
from urllib import request
from django.test import TestCase, RequestFactory
from shift_maker.models import WorkContent, User, Slot, Shift
from django.urls import reverse
import shift_maker.views as views
import datetime
class Assign_lack_slot_TestCase(TestCase):
    def setUp(self):
        self.user=User.objects.create(account_name="testuser1")
        self.workcontent=WorkContent.objects.create(contentname="testcontent",workload=3)
        self.slot=Slot.objects.create(workname="testSlot",content=self.workcontent)
        self.slot2=Slot.objects.create(workname="testSlot2",content=self.workcontent)
        self.slot3=Slot.objects.create(workname="testSlot3",content=self.workcontent,)
        self.factory=RequestFactory()
    def test_assign_lack_slot_twice(self):
        self.request=self.factory.post(reverse("shift_maker:assign_lack",args=[self.slot.pk]))
        self.request.user=self.user
        views.assign_lack_slot(self.request,self.slot.pk)
        views.assign_lack_slot(self.request,self.slot.pk)
        self.assertEqual(self.user.workload_sum, self.workcontent.workload)
    # Setup で作られたインスタンスはメソッドごとに初期化されるっぽい？
    def test_assign_lack_slot_sametime(self):
        print(self.slot.day)        
        self.request=self.factory.post(reverse("shift_maker:assign_lack",args=[self.slot2.pk]))
        self.request.user=self.user
        views.assign_lack_slot(self.request,self.slot.pk)
        views.assign_lack_slot(self.request,self.slot2.pk)
        overlapping_slots=views.overlapping_slots(self.user.assigning_slot.all())
        self.assertFalse(overlapping_slots)
        print(self.user.assigning_slot.all().count())
        self.assertEqual(1,self.user.assigning_slot.all().count())
    
class shift_calculate_Test(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user2=User.objects.create(account_name="testuser2",Block_name="b3")
        cls.user=User.objects.create(account_name="testuser1",Block_name="b3")
        cls.workcontent=WorkContent.objects.create(contentname="testcontent1",workload=0)
        cls.workcontent2=WorkContent.objects.create(contentname="testcontent2",workload=0)
        cls.slot=Slot.objects.create(workname="testSlot",content=cls.workcontent)
        cls.slot2=Slot.objects.create(workname="testSlot2",content=cls.workcontent)
        cls.slot2.day+=datetime.timedelta(days=2)
        cls.slot2.save()
        cls.shift=Shift.objects.create(shift_name="testshift",target="b3")
        cls.factory=RequestFactory()
        cls.request=cls.factory.post(reverse("shift_maker:scheduling",args=[cls.shift.pk]))
    def test_required_number_diff(self):
        self.user.assigned_work.add(self.workcontent,self.workcontent2)
        self.user2.assigned_work.add(self.workcontent,self.workcontent2)
        self.user.assigning_slot.add(self.slot,self.slot2)  
        self.user2.assigning_slot.add(self.slot,self.slot2)
        self.slot.required_number=0
        self.slot.save()
        self.slot2.required_number=2
        self.slot2.save()
        self.shift.slot.add(self.slot,self.slot2)
        views.shift_calculate(self.request,self.shift.pk)
        self.assertEqual(self.slot2.slot_users.all().count(),2)
        self.assertFalse(self.slot.slot_users.all())
        self.assertEqual(self.slot2.slot_users.all().count(),2)
    def test_exp_worker_in(self):
        self.slot.required_number=1
        self.slot.save()
        self.slot2.required_number=1
        self.slot2.content=self.workcontent2
        self.slot2.save()
        self.user.assigned_work.add(self.workcontent)
        self.user2.assigned_work.add(self.workcontent2)
        self.user.assigning_slot.add(self.slot,self.slot2)  
        self.user2.assigning_slot.add(self.slot,self.slot2)
        user1=User.objects.filter(account_name='testuser1')
        user2=User.objects.filter(account_name='testuser2')
        self.shift.slot.add(self.slot,self.slot2)
        views.shift_calculate(self.request,self.shift.pk)
        self.assertQuerysetEqual(self.slot.slot_users.all(),user1)
        self.assertQuerysetEqual(self.slot2.slot_users.all(),user2)
    def test_workload_equality(self):
        self.workcontent.workload=1
        self.workcontent.save()
        self.workcontent2.workload=1
        self.workcontent2.save()
        self.user.assigned_work.add(self.workcontent,self.workcontent2)
        self.user2.assigned_work.add(self.workcontent,self.workcontent2)
        self.user.assigning_slot.add(self.slot,self.slot2)  
        self.user2.assigning_slot.add(self.slot,self.slot2)
        self.slot.required_number=1
        self.slot.save()
        self.slot2.required_number=1
        self.slot2.content=self.workcontent2
        self.slot2.save()        
        self.shift.slot.add(self.slot,self.slot2)
        views.shift_calculate(self.request,self.shift.pk)
        self.assertEqual(self.slot.slot_users.all().count(),1)
        self.assertEqual(self.slot2.slot_users.all().count(),1)
        self.assertFalse(self.slot.slot_users.all()==self.slot2.slot_users.all())
    def test_assigning_sametime(self):
        self.user.assigned_work.add(self.workcontent)
        self.user.assigning_slot.add(self.slot,self.slot2)  
        self.slot.required_number=1
        self.slot.save()
        self.slot2.required_number=1
        self.slot2.day=self.slot.day
        self.slot2.save()
        self.shift.slot.add(self.slot,self.slot2)
        views.shift_calculate(self.request,self.shift.pk)
        self.assertEqual(self.slot.slot_users.all().count()+self.slot2.slot_users.all().count(),1)        
        self.assertTrue(self.user.assigning_slot.all())
        self.assertFalse(self.user2.assigning_slot.all())


