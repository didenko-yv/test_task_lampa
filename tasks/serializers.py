from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from tasks.models import Task


class TaskCreateSerializer(serializers.ModelSerializer):

    status = serializers.IntegerField(min_value=0, max_value=1, required=False)

    class Meta:
        model = Task
        fields = ("id", "name", "description", "status", "created", "user")
        read_only_fields = ("id", "created", "user")


class ListRetrieveTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = "__all__"


class UpdateTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ("name", "description", "status")

    def validate(self, attrs: dict):
        if attrs.get("status") and attrs["status"] not in Task.TASK_STATUS:
            raise ValidationError(
                detail="Value error! The 'status' field must be in the %s"
                % Task.TASK_STATUS
            )
        return attrs


class FilterTaskSerializer(serializers.Serializer):

    DESC: str = "desc"
    ASC: str = "asc"

    status = serializers.IntegerField(
        min_value=0, max_value=1, allow_null=True
    )  # обмеження, тому що поки лише 2 стани що лежать в проміжку 0-1
    name = serializers.CharField(max_length=256, allow_null=True)
    order = serializers.ChoiceField(
        choices={DESC: DESC, ASC: ASC}, default=DESC, allow_null=True
    )
