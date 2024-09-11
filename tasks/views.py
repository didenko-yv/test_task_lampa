from typing import Type

from django.db.models import QuerySet, Q
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.serializers import Serializer

from tasks import serializers
from tasks.models import Task


def gather_query_params(*, serializer: Type[Serializer], request: Request):
    data = {}
    for _field in serializer._declared_fields.keys():
        data[_field] = request.query_params.get(_field)
    query_parameters = serializer(data=data)
    query_parameters.is_valid(raise_exception=True)
    return {field: value for field, value in query_parameters.validated_data.items()}


class TasksListAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.ListRetrieveTaskSerializer

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.TaskCreateSerializer
        return self.serializer_class

    def get_queryset(self):
        return Task.objects.filter(Q(user_id=self.request.user.id) | Q(user_id=None))

    def filter_queryset(self, queryset: QuerySet):
        qp = gather_query_params(
            serializer=serializers.FilterTaskSerializer, request=self.request
        )
        if qp["status"] is not None:
            queryset = queryset.filter(status=qp["status"])

        if qp["name"] is not None:
            queryset = queryset.filter(name__contains=qp["name"])

        if qp["order"] is serializers.FilterTaskSerializer.ASC:
            return queryset.order_by("created")
        return queryset.order_by("-created")


class TaskDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = serializers.ListRetrieveTaskSerializer

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return serializers.UpdateTaskSerializer
        elif self.request.method == "GET":
            return self.serializer_class
        raise ValueError("Unknown action")
