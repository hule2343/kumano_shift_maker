from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView 
from . import views

app_name = 'shift_maker'
urlpatterns = [
    path('mypage/',views.MyPageView.as_view(),name='mypage'),
    path('mypage/recruitment/<int:pk>/',views.shift_recruit_view,name='recruit'),
    path('mypage/recruitment/<int:pk>/answer/',views.shift_receive_answer_view,name='answer'),
    path('mypage/recruit/<int:pk>/', views.RecruitDetailView.as_view(),name='recruit_detail'),
    path('mypage/recruit/<int:pk>/calculate/',views.shift_calculate,name='scheduling'),
    path('mypage/recruit/<int:pk>/calculate/result',views.shift_calculate_result,name='result_schedule'),
    path('mypage/createslot/',views.CreateSlotView.as_view(),name='createslot'),
    path('mypage/createshift/',views.CreateShift.as_view(),name='createshift'),
    path('mypage/createtemplate/',views.CreateShiftTemplate.as_view(),name='createshifttemplate'),
    path('mypage/shifttempform/',views.ShiftFormFromTemplateView.as_view(),name='shift_create_form_template'),
    path('mypage/shifttempform/creshiftfromtemp/',views.shift_from_template,name='shift_from_template'),
    path('mypage/assign_lack/<int:pk>',views.LackSlotDetailView.as_view(),name='lack_slot_detail'),
    path('mypage/assign_lack/<int:pk>/assign/',views.assign_lack_slot,name='assign_lack'),
    path('mypage/delete/<int:pk>/',views.AssigningSlotDetailView.as_view(),name="slot_delete_detail"),
    path('mypage/delete/<int:pk>/delete/',views.delete_assigned_slot,name='slot_delete'),
    path('mypage/delete_booking/<int:pk>/',views.BookingSlotDetailView.as_view(),name='booking_slot_detail'),
    path('mypage/delete_booking/<int:pk>/delete/',views.delete_booking_slot,name='booking_slot_delete'),
    path('login/', LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout')
]