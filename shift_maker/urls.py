from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView 
from . import views

app_name = 'shift_maker'
urlpatterns = [
    path('mypage/',views.MyPageView.as_view(),name='mypage'),
    path('mypage/recruitment/<int:pk>/',views.shift_recruit_view,name='recruit'),
    path('mypage/recruitment/<int:pk>/answer/',views.shift_receive_answer_view,name='answer'),
    path('mypage/createslot/',views.CreateSlotView.as_view(),name='createslot'),
    path('mypage/createshift/',views.CreateShift.as_view(),name='createshift'),
    path('mypage/createtemplate/',views.CreateShiftTemplate.as_view(),name='createshifttemplate'),
    path('mypage/shifttempform/',views.ShiftFormFromTemplateView.as_view(),name='shift_create_form_template'),
    path('mypage/shifttempform/creshiftfromtemp/',views.shift_from_template,name='shift_from_template'),
    path('login/', LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout')
]