from http.client import ImproperConnectionState
from urllib import request
from django.test import TestCase, RequestFactory
from shift_maker.models import WorkContent, User, Slot
from django.urls import reverse
import shift_maker.views as views

class Assign_lack_slot_TestCase(TestCase):
    def setUp(self):
        self.user=User.objects.create(account_name="testuser1")
        self.workcontent=WorkContent.objects.create(contentname="testcontent",workload=3)
        self.slot=Slot.objects.create(workname="testSlot",content=self.workcontent)
        self.slot2=Slot.objects.create(workname="testSlot2",content=self.workcontent)
        self.factory=RequestFactory()
    def test_assign_lack_slot_twice(self):
        self.request=self.factory.post(reverse("shift_maker:assign_lack",args=[self.slot.pk]))
        self.request.user=self.user
        views.assign_lack_slot(self.request,self.slot.pk)
        views.assign_lack_slot(self.request,self.slot.pk)
        self.assertEqual(self.user.workload_sum, self.workcontent.workload)
    def test_assign_lack_slot_sametime(self):
        self.request=self.factory.post(reverse("shift_maker:assign_lack",args=[self.slot2.pk]))
        views.assign_lack_slot(self.request,self.slot.pk)
        overlapping_slots=views.overlapping_slots(self.user.assigning_slot.all())
        self.assertFalse(overlapping_slots)