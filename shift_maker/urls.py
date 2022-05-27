from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from django.views.generic import TemplateView


app_name = 'shift_maker'
urlpatterns = [
    path('mypage/',views.MyPageView.as_view(),name='mypage'),
    path('mypage/recruitment/<int:pk>/',views.shift_recruit_view,name='recruit'),
    path('mypage/recruitment/<int:pk>/answer/',views.shift_receive_answer_view,name='answer'),
    path('mypage/recruit/<int:pk>/', views.shift_recruit_detail,name='recruit_detail'),
    path('mypage/recruit/<int:pk>/calculate/',views.shift_calculate,name='scheduling'),
    path('mypage/recruit/<int:pk>/calculate/result',views.shift_calculate_result,name='result_schedule'),
    path('mypage/memberlist/',views.BlockMemberList.as_view(),name='memberlist'),
    path('mypage/contentlist/',views.WorkContentList.as_view(),name='contentlist'),
    path('mypage/contentlist/assign/<int:pk>/',views.assign_content,name='assign_content'),
    path('mypage/createpage/',TemplateView.as_view(template_name='shift_maker/createpage.html'),name='create_page'),
    path('mypage/createpage/createslot/',views.CreateSlot.as_view(),name='createslot'),
    path('mypage/createpage/createshift/',views.CreateShift.as_view(),name='createshift'),
    path('mypage/createpage/createtemplate/',views.CreateShiftTemplate.as_view(),name='createshifttemplate'),
    path('mypage/createpage/shifttempform/',views.ShiftFormFromTemplateView.as_view(),name='shift_create_form_template'),
    path('mypage/shifttempform/creshiftfromtemp/',views.shift_from_template,name='shift_from_template'),
    path('mypage/assign_lack/<int:pk>/assign/',views.assign_lack_slot,name='assign_lack'),
    path('mypage/assign_slot/<int:pk>/assign/',views.assign_slot,name='assign'),
    path('mypage/replace/<int:slot_id>/<int:user_id>/',views.replace_slot,name='replace'),
    path('mypage/delete/<int:pk>/delete/',views.delete_assigned_slot,name='slot_delete'),
    path('mypage/delete_booking/<int:pk>/delete/',views.delete_booking_slot,name='booking_slot_delete'),
    path('login/', LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),
]