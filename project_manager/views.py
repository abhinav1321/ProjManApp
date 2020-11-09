from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from datetime import datetime
from .models import Card, List, Board, Team, ExtendedUser, FileUpload, CardChecklist, TeamMembers
from .serializers import CardSerializer, ListSerializer, BoardSerializer,\
    ExtendedUserSerializer, TeamSerializer, TeamMembersSerializer, CardChecklistSerializer
from .utils import change_card_location, change_card_list, sign_in, add_user_in_card, delete_user_in_card
from .utils import check_user_logged, board_components, list_components, get_list_data, edit_board_data
from .utils import get_team, create_team, add_team_member, remove_team_member, get_files, upload_file, reset_priority_on_deletion
from .utils import create_checklist_item, edit_checklist_item, delete_checklist_item, available_user_for_card
from .utils import extend_user
from wsgiref.util import FileWrapper
import os


# Create your views here.
def index(request):
    if request.method == 'POST':
        login = sign_in(request)
        if login[0] == 'login failed':
            return HttpResponse('login failed')
        username = check_user_logged(request)

        return render(request, 'project_manager/index.html', {'username': username})

    elif request.method == 'GET':
        sign_in(request)
        username = check_user_logged(request)

        return render(request, 'project_manager/index.html', {'username': username})


def sign_up(request):
    if 'username' in request.GET.keys():
        username = request.GET.get('username')
        first_name = request.GET.get('first_name')
        last_name = request.GET.get('last_name')
        email = request.GET.get('email')
        password = request.GET.get('password')
        gender = request.GET.get('gender')
        contact = request.GET.get('contact')
        account_type = request.GET.get('account')

        try:
            user = User.objects.create_user(username, email, password)
            try:
                extend_user(user.id, first_name, last_name, gender, account_type)
            except Exception as error:
                print(error)
        except Exception as e:
            print(e)
        else:
            return render(request, 'project_manager/sign_up.html')

    return render(request, 'project_manager/sign_up.html')


# Boards View
def boards(request):
    username = check_user_logged(request)
    if not username == 'None':
        # Utils Function edit_board_data() taking care of POST, UPDATE and DELETE
        message, errors = edit_board_data(request)

        board_data = board_components(username)
        return render(request, 'project_manager/boards.html', {
                                                            'username': username,
                                                            'board_data': board_data,
                                                            'errors': errors})


def get_list(request):
    username = check_user_logged(request)
    if not username == 'None':
        if request.method == 'POST':
            data = request.POST.copy()
            errors = ''
            board_id = data['board_id']
            del data['csrfmiddlewaretoken']
            list_data = get_list_data(board_id)
            team = get_team(board_id=board_id)
            board_name = Board.objects.get(pk=data['board_id']).board_name
            if len(team) == 0:
                team_create = create_team(board_id, 'Team '+str(board_name))
                print(team_create)
                team = get_team(board_id=board_id)
            return render(request, 'project_manager/get_list.html', {
                                                                    'username': username,
                                                                    'list_data': list_data,
                                                                    'board_id': board_id,
                                                                    'errors': errors,
                                                                    'teams': team,
                                                                    'board_name': board_name
                                                                    })
    else:
        return HttpResponse('')


# Post and Patch list
def add_or_update_list(request):
    username = check_user_logged(request)
    if username != 'None':
        board_id = ''
        errors = ''

        if request.method == 'POST':

            data = request.POST.copy()
            data['created_date'] = datetime.now()
            del data['csrfmiddlewaretoken']
            board_id = data['board_id']
            board_name = Board.objects.get(pk=data['board_id']).board_name

            if 'list_id' in data.keys():
                list_id = data['list_id']
                list_model_object = List.objects.get(pk=list_id)
                list_serializer = ListSerializer(list_model_object, data=data)

            else:
                board_obj = Board.objects.get(pk=board_id)
                data['owner'] = board_id
                del data['board_id']
                list_serializer = ListSerializer(data=data)

            if list_serializer.is_valid(raise_exception=True):
                list_serializer.save()
            else:
                errors = list_serializer.errors

        if request.method == 'GET':
            board_id = request.GET.get('board_id')
            list_id = request.GET.get('list_id')
            board_name = Board.objects.get(pk=board_id).board_name
            try:
                List.objects.get(pk=list_id).delete()
            except:
                errors = 'Could not delete'

        list_data = get_list_data(board_id)
        team = get_team(board_id=board_id)
        return render(request, 'project_manager/get_list.html', {
                                                            'username': username,
                                                            'list_data': list_data,
                                                            'board_id': board_id,
                                                            'errors': errors,
                                                            'team': team,
                                                            'board_name': board_name
                                                                })


# List Details contains all the cards list contains
def list_details(request):
    username = check_user_logged(request)
    errors = ''
    if username != 'None':
        # Delete A Card
        if request.method == "GET":
            list_id = request.GET.get('list_id')
            card_id = request.GET.get('card_id')
            card_obj = Card.objects.get(pk=card_id)
            reset_priority_on_deletion(card_obj)
            card_obj.delete()

        # Add Card, Edit card
        else:
            data = request.POST.copy()
            print(data, 'data here')
            list_id = data['list_id']
            del data['csrfmiddlewaretoken']
            # card_name in request, if a card to be added or updated
            if 'card_name' in data.keys():
                # Edit Card
                if 'card_id' in data.keys():
                    # changing priority
                    if 'priority' in data.keys() and data['priority'] != '':
                        change_card_location(data['card_id'], data['priority'])
                    data['fk_list'] = data['list_id']
                    card_obj = Card.objects.get(pk=data['card_id'])

                    del data['list_id']
                    del data['card_id']
                    serializer = CardSerializer(card_obj, data=data)
                    if serializer.is_valid():
                        serializer.save()
                    errors = serializer.errors
                    print(errors)

                # Add new Card
                else:
                    list_obj = List.objects.get(pk=list_id)
                    data['fk_list'] = list_obj.id
                    del data['list_id']
                    data['due_date'] = datetime.strptime(data['due_date'], '%Y-%m-%d')
                    serializer = CardSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                    errors = serializer.errors
                    change_card_list(serializer.data['id'], list_id, new_card=True)

        objects = Card.objects.filter(**{'fk_list': list_id})
        cards = CardSerializer(objects, many=True)
        return render(request, 'project_manager/list_details.html', {
                                                    'list_id': list_id,
                                                    'username': username,
                                                    'cards': cards.data,
                                                    'errors': errors,
                                                    })


def teams(request):
    username = check_user_logged(request)
    search_result = []
    if username != 'None':
        data = request.POST.copy()

        if 'team_id' not in data.keys():
            board_id = data['board_id']
            team_obj = Team.objects.get(from_board=board_id)
            team_id = team_obj.id
        else:
            team_id = data['team_id']
        del data['csrfmiddlewaretoken']
        if 'to_add' in data.keys():
            add_team_member(team_id, data['to_add'], data['role'])
        if 'to_remove' in data.keys():
            remove_team_member(team_id, data['to_remove'])

        team_obj = Team.objects.get(pk=team_id)
        team_data = get_team(team_id=team_obj.id)
        team_data = TeamMembersSerializer(team_data, many=True)

        if 'search_by_name' in data.keys():
            search_by_name = data['search_by_name']
            query_first = ExtendedUser.objects.filter(First_name__contains=search_by_name)
            query_last = ExtendedUser.objects.filter(Last_name__contains=search_by_name)
            if len(query_first) > 0:
                query_first = ExtendedUserSerializer(query_first, many=True).data
                search_result = search_result + query_first
            if len(query_last) > 0:
                query_last = ExtendedUserSerializer(query_last, many=True).data
                search_result = search_result + query_last

        if 'search_by_id' in data.keys():
            search_by_id = data['search_by_id']
            query_obj = ExtendedUser.objects.filter(pk=search_by_id)
            if len(query_obj) > 0:
                query_id = ExtendedUserSerializer(query_obj, many=True).data
                search_result = search_result + query_id

        return render(request, 'project_manager/team.html', {
                                                             'username': username,
                                                             'team_id': team_id,
                                                             'search_result': search_result,
                                                             'team_data': team_data.data
                                                             })


def file(request):
    username = check_user_logged(request)
    if username != 'None':
        data = request.POST.copy()
        card_id = data['card_id']
        if 'file_name' in data.keys():
            to_upload_file = request.FILES['file_upload']
            upload_file(card_id, data['file_name'], to_upload_file)
        card_name = Card.objects.get(pk=card_id).card_name
        files = get_files(card_id)
        return render(request, 'project_manager/file.html', {'files': files,
                                                             'card_id': card_id,
                                                             'card_name': card_name
                                                             })


def download_file(request):
    file_id = request.POST.get('file_id')
    file_obj = FileUpload.objects.get(pk=file_id)

    wrapper = FileWrapper(open(str(file_obj.file), 'rb'))
    response = HttpResponse(wrapper, content_type='application/force-download')
    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(str(file_obj.file))
    return response


def change_list(request):
    username = check_user_logged(request)
    if username != 'None':
        data = request.POST.copy()
        card_id = data['card_id']
        current_list = Card.objects.get(pk=card_id).fk_list.id
        board_id = List.objects.get(pk=current_list).owner.id
        lists = get_list_data(board_id)

        if 'list_id' in data.keys():
            change_card_list(card_id, new_list_id=data['list_id'])

        return render(request, 'project_manager/change_list.html', {'lists': lists,
                                                                    'card_id': card_id,
                                                                    'current_list': current_list,
                                                                    'username': username})


def card_checklist_view(request):
    username = check_user_logged(request)
    if username != 'None':
        data = request.POST.copy()
        card_id = data['card_id']
        # Create Element
        if 'to_create' in data.keys():
            element_check = True if data['checked'] == 'True' else False
            create_checklist_item(card_id, data['to_create'], element_check)
        # Update
        if 'to_edit' in data.keys():
            element_check = True if data['checked'] == 'True' else False
            edit_checklist_item(data['checklist_id'], data['to_edit'], element_check)
        # Delete to_delete as checklist.id
        if 'to_delete' in data.keys():
            delete_checklist_item(data['to_delete'])

        obj = CardChecklist.objects.filter(card=card_id)

        serializer = CardChecklistSerializer(obj, many=True)

        return render(request, 'project_manager/checklist.html', {
                                                                    'checklist': serializer.data,
                                                                    'card_id': card_id,
                                                                    'username': username})


def add_user_to_card(request):
    data = request.POST.copy()
    card_id = data['card_id']
    available_user = available_user_for_card(card_id)
    if 'new_user_id' in data.keys():
        if not data['new_user_id'] == '':
            add_user_in_card(card_id, data['new_user_id'])
    if 'delete_user' in data.keys():
        delete_user_in_card(card_id, data['delete_user'])

    users = Card.objects.get(pk=card_id).user_list
    if users is not None and users != '' and users != ' ':
        users = users.split(' ')
    else:
        users = []
    return render(request, 'project_manager/add_user_to_card.html', {'available_user': available_user,
                                                                     'card_id': card_id,
                                                                     'users': users})
