from django.test import TestCase
from shift_maker.models import User

class PostModelTests(TestCase):

    def test_is_empty(self):
        """初期状態では何も登録されていないことをチェック"""  
        saved_user = User.objects.all()
        self.assertEqual(saved_user.count(), 0)
    
    def test_is_count_one(self):
        user=User(account_name="testuser",password="modeltest123")
        user.save()
        users=User.objects.all()
        self.assertEqual(users.count(),1)
    
    def test_saving_and_retrieving_user(self):
        user=User()
        Block_name="b3"
        room_number=310
        account_name="testuser"
        password="modeltest123"
        user.Block_name=Block_name
        user.room_number=room_number
        user.account_name=account_name
        user.password=password
        user.save()
        users=User.objects.all()
        actual_user=users[0]
        self.assertEqual(actual_user.Block_name,Block_name)
        self.assertEqual(actual_user.room_number,room_number)
        self.assertEqual(actual_user.account_name,account_name)
        self.assertEqual(actual_user.password,password)
        self.assertEqual(actual_user.workload_sum,0)

    




