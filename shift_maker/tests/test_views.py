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
        self.request=RequestFactory.post(reverse("shift_maker:assign_lack",args=[self.slot.pk]))
    def test_assign_lack_slot(self):
        self.request.user=self.user
        views.assign_lack_slot(self.request)
        views.assign_lack_slot(self.request)
        self.assertEqual(self.user.workload, self.workcontent.workload)

