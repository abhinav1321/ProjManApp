from django.urls import path, include
from .import views

urlpatterns = [

    path('', views.index, name='index'),
    path('boards', views.boards, name='boards'),
    path('get_list', views.get_list, name='get_list'),
    path('add_or_update_list', views.add_or_update_list, name='add_or_update_list'),
    path('list_details', views.list_details, name='list_details'),
    path('teams', views.teams, name='teams'),
    path('file', views.file, name='file'),
    path('download_file', views.download_file, name='download_file'),
    path('change_list', views.change_list, name='change_list'),
    path('card_checklist_view', views.card_checklist_view, name='card_checklist_view'),
    path('add_user_to_card', views.add_user_to_card, name='add_user_to_card'),
    path('sign_up', views.sign_up, name='sign_up'),

]
