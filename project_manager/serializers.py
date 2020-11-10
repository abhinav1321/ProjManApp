from rest_framework import serializers
from .models import Board, Card, ExtendedUser, List, Team, TeamMembers, CardChecklist


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'board_name', 'board_color', 'created_date', 'owner']


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'card_name', 'description',  'user_list', 'priority', 'fk_list']


class ExtendedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtendedUser
        fields = ['id', 'First_name', 'Last_name', 'Gender', 'account_type', 'user']


class ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = ['id', 'owner', 'list_name', 'created_date']


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'from_board', 'team_name']


class TeamMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMembers
        fields = ['team', 'u_id', 'role']


class CardChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardChecklist
        fields = ['id', 'card', 'element', 'checked']
