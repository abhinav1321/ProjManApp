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
    """
    Index Page is containing login method, new users May SignUp From a link to sign_up
    """
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
    """
    Initial Page to Sign Up. Containing Form at sign_up.html template,
    Gets redirect back-to same page after processing the request

    After successful creation on user, it calls Util function
                extend_user(user.id, first_name, last_name, gender, account_type)
                To Extend the Auth user to ExtendedUser Model
    """
    message = ''
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
                message = 'Account Created Successfully, Please Login '
            except Exception as error:
                message = error
        except Exception as e:
            message = e
        else:
            return render(request, 'project_manager/sign_up.html', {'message': message})

    return render(request, 'project_manager/sign_up.html', {'message': message})


# Boards View
def boards(request):
    """
    Landing Page for boards,
     1. "board_data" function Get all boards for current user.
     2. "edit_board_data" function handles POST, UPDATE and DELETE of a board
    """
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
    """
    Gets list data for a board,
    Utils Functions:
    1. get_list_data() - inputs board_id and gets all lists for the board
    2. get_team() - If given board id, returns team data for the board,
                    if given team_id, returns data for the team
    3. create_team() - creates a new team automatically for the board
    4. get_user_logged() - checks if the user is logged in, returns username or 'None'
    """
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
    """
    This view helps with
    1. addition of a new list: POST Method:
                                Input variables - board_id, list_name
    2. Deletion of a list : GET method
                            Input variables - Board_id, list id
    3. Utils Function used - a. get_list_data(board_id)
                                    : returns all the lists for current board
                             b. get_team(board_id)
                                    : returns team_data
                             c. check_user_logged:
                                    : checks for user session and returns username
                                        if not logged in - returns 'None'
    This View directs to get_list/html template

    """
    username = check_user_logged(request)
    if username != 'None':
        board_id = ''
        errors = ''

        if request.method == 'POST':

            data = request.POST.copy()
            print(data)
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
    """
    Contains details of the list, i.e. Cards included inside it
    List details contains all the card inside a list
    Methods:
        GET Method - Used to Delete a card
                    inputs List_id and Card_id in requests

        POST Method: request method must have following variables
                    To Edit Card  :- card_id, card_name, description, priority (fields are auto-populated in html)
                    To Add a New Card: Card_name, Description, Due Date
        util functions:
                1. change_card_location : a. called when changing th priority of
                                           card i.e. -> moving a card within the list

                2. change card list --->    called when adding a new card
    """
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
                    if data['due_date'] == '':
                        data['due_date'] = Card.objects.get(id=data['card_id']).due_date
                    else:
                        data['due_date'] = datetime.strptime(data['due_date'], '%Y-%m-%d')

                    card_obj = Card.objects.get(pk=data['card_id'])
                    print(data, 'data')
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
    """
        Team View outputs requested team data,
            Can be accessed from (get_list.html) page with board id
            or can be accesed from team.html page, with team_id

        functionalities:
              Can search for a member (by First_name or by last_name), or by extended_u_id

              Can add a searched member,
                         with input variables(inside request):    a. board_id
                                                                  b. team_id
                                                                  c. to_add - (extended user id)
                                                                  d. role  - (admin or member)
              Can delete a present member :
                        with input variables(inside request)      a. team_id
                                                                  b. to_delete (extended user id)

        Utils functions used :  get_team(team_id)
    """
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
    """
        For Adding Files in card and view added files

            Input Variables(inside request)
                                : card_id , file_name, file itself --> for uploading a file
                                : card_id   -- > for getting files already uploaded
            Utils Functions Used
                                :get_files(card_id) -- returns file data

    """
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
    """ for Downloading the selected file ->  from file.html"""

    file_id = request.POST.get('file_id')
    file_obj = FileUpload.objects.get(pk=file_id)

    wrapper = FileWrapper(open(str(file_obj.file), 'rb'))
    response = HttpResponse(wrapper, content_type='application/force-download')
    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(str(file_obj.file))
    return response


def change_list(request):
    """
    changing list of a card from current list to any other list in the board
            input variables methods :
                                a. card_id, list_id (new_list) ->moves input Card to the given list_id
                                                                (by changing foreign key to the given list)

                                b. card_id (without list_id) -> gives back data for all the list in board

    util Function : get_list_data(board_id) -> gets all the lists available for current board
    """
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
    """
        Create, Update and Delete a checklist element
            variables(inside request):  card_id -     simply view all elements
                                        card_id, to_edit(checklist_id), checked(True,False)  -Updation
                                        card_id, to_delete(checklist_id)   -- Deletion
                                        card_id, to_create
    """
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
    """
        Adding/Deleting user (extended_userid) to card
            input variables  : card_id, new_user_id (extended uid) -  adding a new user
                             : card_id, delete_user (extended uid)  - deleting a user

        Util Function - available_user_for_card(card_id) - gets the users available on current board
                                                                    (which can be extended to card)
     """
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
