from .serializers import CardSerializer, ListSerializer, BoardSerializer,\
                    TeamSerializer, CardChecklistSerializer, ExtendedUserSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Card, List, Board, Team, ExtendedUser, FileUpload, TeamMembers, CardChecklist
from django.shortcuts import redirect
import json
import re
from datetime import datetime


def sign_in(request):
    username, create_session = None, None
    if request.method == 'GET':
        if 'action' in request.GET and request.GET['action'] == 'sign_out':
            if request.session.has_key('username'):
                request.session.flush()
            return redirect('/')

    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user:
            create_session = request.session
            create_session['username'] = user.username
            create_session.set_expiry(10000)
            return username, create_session
        else:
            return 'login failed', create_session


def check_user_logged(request):
    username = 'None'
    if request.session.has_key('username'):
        username = request.session['username']
    return username


def board_components(username):
    user = User.objects.filter(username=username)[0]
    extended_user_name = ExtendedUser.objects.filter(user=user)[0]
    board = Board.objects.filter(owner=extended_user_name)
    components = BoardSerializer(board, many=True)
    return components.data


def get_list_data(board_id):
    list_data = list_components(board_id)

    for item in list_data:
        objects = Card.objects.filter(**{'fk_list': item['id']})
        cards_in_the_list = []
        for obj in objects:
            cards_in_the_list.append(
                {
                    'card_id': obj.id,
                    'card_name': obj.card_name,
                    'due_date': obj.due_date,
                    'priority': obj.priority
                }
            )
        item['cards_in_the_list'] = cards_in_the_list
    return list_data


def list_components(board_id):
    board = Board.objects.filter(pk=board_id)
    list_objects = List.objects.filter(owner=board[0])
    components = ListSerializer(list_objects, many=True)
    return components.data


def reset_priority_on_deletion(card_obj):
    cards_in_current_list = Card.objects.filter(fk_list=card_obj.fk_list.id).order_by('priority')
    for card in cards_in_current_list:
        if card.priority > card_obj.priority:
            Card.objects.filter(id=card.id).update(priority=card.priority - 1)


def change_card_list(card_id, new_list_id, new_card=False):
    # This function is also called after creation of new card.
    card_obj = Card.objects.get(pk=card_id)

    # fail- safe,if same request done twice
    if card_obj.fk_list != new_list_id or new_card is True:

        if new_card is False:
            # Resetting priorities of current list if not a new card
            reset_priority_on_deletion(card_obj)

        list_obj = List.objects.get(pk=new_list_id)
        query = Card.objects.filter(fk_list=list_obj).order_by('priority')
        print(len(query))
        if len(query) == 0:
            Card.objects.filter(id=card_id).update(fk_list=list_obj, priority=1)
        else:
            Card.objects.filter(id=card_id).update(fk_list=list_obj, priority=len(query))


def get_team(board_id=None, team_id=None):
    members = []
    if board_id is not None:
        member_list = []
        board_obj = Board.objects.get(pk=board_id)
        team_obj = Team.objects.filter(from_board=board_obj.id)
        for team in team_obj:
            members = TeamMembers.objects.filter(team=team.id)
            member_list.append(members)
        return members
    elif team_id is not None:
        members = TeamMembers.objects.filter(team=team_id)
        return members


def create_team(board_id, team_name='New Team'):
    board_obj = Board.objects.get(pk=board_id)
    data = {}
    data['team_name'] = team_name
    data['from_board'] = board_obj.id
    serializer = TeamSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
    return serializer.errors


def add_team_member(team_id, extended_uid, role='member'):
    team_obj = Team.objects.get(pk=team_id)
    team_member = TeamMembers.objects.create(team=team_obj, role=role, u_id=extended_uid)
    team_member.save()


def remove_team_member(team_id, extended_uid):
    team_obj = Team.objects.get(pk=team_id)
    members = TeamMembers.objects.filter(team=team_obj).filter(u_id=extended_uid)
    members.delete()


def get_files(card_id):
    file_obj = FileUpload.objects.filter(fk_card=card_id)
    file_list = []
    for file in file_obj:
        file = {'id': file.id, 'file_name': file.file_name}
        file_list.append(file)
    return file_list


def upload_file(card_id, file_name, file_data):
    card_obj = Card.objects.get(pk=card_id)
    file = FileUpload.objects.create(file_name=file_name, file=file_data, fk_card=card_obj)
    file.save()


def edit_board_data(request):
    username = check_user_logged(request)
    errors = message = ''
    if request.method == 'POST':
        data = request.POST.copy()
        data['created_date'] = datetime.now()
        del data['csrfmiddlewaretoken']

        if 'id' in data.keys():
            # Patch Method will have id in it
            model_object = Board.objects.get(pk=data['id'])
            data_serializer = BoardSerializer(model_object, data=data)
        else:
            # Post Method- Adding a new board
            user = User.objects.get(username=username)
            extended_user = ExtendedUser.objects.get(user=user)
            data['owner'] = extended_user.id
            data_serializer = BoardSerializer(data=data)

        if data_serializer.is_valid(raise_exception=True):
            data_serializer.save()
            message = 'Update Successful'
        else:
            errors = data_serializer.errors
    # Delete a Board
    elif request.method == 'GET':
        try:
            board_id = request.GET.get('board_id')
            Board.objects.get(pk=board_id).delete()
            message = 'Deletion Successful'
        except:
            errors = 'Could Not Delete'
    return message, errors


def change_card_location(card_id, new_priority):
    card_id, new_priority = int(card_id), int(new_priority)
    card_obj = Card.objects.get(pk=card_id)
    list_name = card_obj.fk_list
    list_obj = List.objects.filter(id=list_name.id)[0]
    all_cards = Card.objects.filter(**{'fk_list': list_obj})
    result = CardSerializer(all_cards, many=True)
    result = sorted(result.data, key=lambda x: x['priority'])

    current = -1
    if current < 0:
        current = result[-1]['priority'] + 1
        for a in result:
            if a['id'] == card_id:
                current = a['priority']

    if current > new_priority:
        for i in range(1, len(result)+1):
            if i < new_priority:
                pass
            elif (i >= new_priority) and (i < current):
                result[i-1]['priority'] += 1
            elif i > current:
                result[i-1]['priority'] -= 1
    elif new_priority > current:
        for i in range(1, len(result)+1):
            if i < current:
                pass
            elif (i > current) and (i <= new_priority):
                result[i-1]['priority'] -= 1
            elif i > new_priority:
                pass
    for a in result:
        if a['id'] == card_id:
            a['priority'] = new_priority

    error = []
    for element in result:
        obj = Card.objects.get(pk=element['id'])
        card_serializer = CardSerializer(obj, data=element)
        if card_serializer.is_valid():
            card_serializer.save()
            error = card_serializer.errors
        else:
            error.append(error)


def create_checklist_item(card,  element, checked):
    card = Card.objects.get(pk=card).id
    data = {'card': card, 'element': element, 'checked': checked}
    serializer = CardChecklistSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
    print('saved', serializer.data)


def edit_checklist_item(checklist_id, element, checked):
    obj = CardChecklist.objects.get(pk=checklist_id)

    data = {'id': checklist_id, 'element': element, 'checked': checked, 'card': obj.card.id}
    serializer = CardChecklistSerializer(obj, data=data)
    if serializer.is_valid():
        serializer.save()
    print(serializer.errors)


def delete_checklist_item(checklist_id):
    obj = CardChecklist(pk=checklist_id)
    if obj:
        obj.delete()


def available_user_for_card(card_id):
    try:
        board_id = Card.objects.get(pk=card_id).fk_list.owner.id
        team_object = Team.objects.get(from_board=board_id)
        members = TeamMembers.objects.filter(team=team_object.id)
        available_user_list = []
        for m in members:

            user_object = ExtendedUser.objects.get(pk=m.u_id)
            available_user = {'id': user_object.id,
                              'First_name': user_object.First_name,
                              'Last_name': user_object.Last_name,
                              'role': m.role}

            available_user_list.append(available_user)

        return available_user_list
    except Exception as e:
        print(e)


def add_user_in_card(card_id, new_user_id):
    card_obj = Card.objects.filter(pk=card_id)
    users = card_obj[0].user_list
    try:
        if ExtendedUser.objects.get(pk=new_user_id):
            if users is None:
                users = new_user_id
            else:
                users = str(users).split(' ')
                if new_user_id not in users:
                    users = users + [new_user_id]
                    users = ' '.join([str(user) for user in users])
            users = users.strip()
            card_obj.update(user_list=users)

    except Exception as e:
        print(e)


def delete_user_in_card(card_id, user_id):
    print('here')
    card_obj = Card.objects.filter(pk=card_id)
    users = card_obj[0].user_list
    users = str(users).split(' ')
    if user_id in users:
        index = users.index(user_id)
        users.pop(index)
    users = ' '.join([str(user) for user in users])
    card_obj.update(user_list=users)


def extend_user(user_obj, first_name, last_name, gender,  account_type):
    account = 2
    if account_type == 'free':
        account = 2
    if account_type == 'premium':
        account = 1
    data = {
        'user': user_obj,
        'First_name': first_name,
        'Last_name': last_name,
        'Gender': gender,
        'account_type': account
        }
    print(data)
    serializer = ExtendedUserSerializer(data=data)
    if serializer.is_valid():
        print('savingg')
        serializer.save()
    print(serializer.errors)
