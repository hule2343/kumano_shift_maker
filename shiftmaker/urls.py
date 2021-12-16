from django.urls import path

from . import views

app_name = 'shift_maker'
urlpatterns = [
    path('mypage/<int:pk>/',view.UserView.as_view(),name='mypage')
    path('mypage/<int:pk>/recruitment/<int:pk>/',view.shift_recruit_view,name='recruit')
    path('mypage/<int:pk>/recruitment/<int:pk>/answer/',view.shift_receive_answer_view,name='answer')
    path('mypage/<int:pk>/createslot/',view.CreateSlotView.as_view(),name='createslot')
    path('mypage/<int:pk>/createshift/',view.CreateShift.as_view(),name='createshift')
    path('mypage/<int:pk>/createtemplate/',view.CreateShiftTemplate.as_view(),name='createshifttemplate')

    path('mypage/<int:pk>/slot/<int:pk>/',,)
    path('shifttempform/',view.ShiftFormFromTemplateView.as_view(),name='shift_create_form_template')
    path('creshiftfromtemp/',view.shift_from_template,name='shift_from_template')
    path()
]