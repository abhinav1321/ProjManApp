from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class ExtendedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    First_name = models.CharField(max_length=100)
    Last_name = models.CharField(max_length=100)
    Gender = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    Phone_number = models.CharField(max_length=100)
    account_type = models.CharField(max_length=10,
                                    choices=[('1', 'premium'), ('2', 'free')],
                                    default='1')


color_list = [
    ('1', 'red'),
    ('2', 'white'),
    ('3', 'blue'),
]


class Board(models.Model):
    owner = models.ForeignKey(ExtendedUser, on_delete=models.SET_NULL, null=True)
    board_name = models.CharField(max_length=50)
    board_color = models.CharField(max_length=10, choices=color_list, default='1')
    created_date = models.DateTimeField()

    def __str__(self):
        return self.board_name


class List(models.Model):
    owner = models.ForeignKey(Board, on_delete=models.CASCADE)
    list_name = models.CharField(max_length=50)
    created_date = models.DateTimeField()

    def __str__(self):
        return self.list_name


class Team(models.Model):
    from_board = models.OneToOneField(Board, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=50)
    # A list of lists, [[Extended_uid,'admin'],[Extended_uid,'member'],[Extended_uid,'member']]
    # members = models.JSONField(default=dict, null=True)


class TeamMembers(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    u_id = models.CharField(max_length=50)
    role = models.CharField(max_length=50, default="member")


class Card(models.Model):
    fk_list = models.ForeignKey(List, on_delete=models.CASCADE)
    card_name = models.CharField(max_length=50)
    description = models.TextField(max_length=300)
    due_date = models.DateTimeField(auto_now_add=True)
    user_list = models.TextField(null=True)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return self.card_name


class CardChecklist(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    element = models.CharField(max_length=50)
    checked = models.BooleanField(default=False)


class FileUpload(models.Model):
    fk_card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='file/%Y/%m/%d')
    file_name = models.CharField(max_length=50, default='Uploaded_file')
