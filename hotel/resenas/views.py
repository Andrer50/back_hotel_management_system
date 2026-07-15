from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg

from ..models import Resena
from ..utils import ApiResponse
from .permissions import IsStaffAuthenticated, IsAdministrador
from .serializers import (
    ResenaListSerializer,
    ResenaCreateSerializer,
    ResenaResponderSerializer,
    ResenaModerarSerializer,
)


class ResenaListCreateView(generics.ListCreateAPIView):
    queryset = Resena.objects.all()
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return Resena.objects.filter(es_inapropiada=False).order_by('-fecha_creacion')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ResenaCreateSerializer
        return ResenaListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsStaffAuthenticated()]
        return [permissions.AllowAny()]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ResenaListSerializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = ResenaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resena = serializer.save()
        out = ResenaListSerializer(resena)
        return ApiResponse.success(data=out.data, message='Reseña creada', status_code=status.HTTP_201_CREATED)


class ResenaPromedioView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        avg = Resena.objects.filter(es_inapropiada=False).aggregate(Avg('calificacion'))['calificacion__avg']
        promedio = float(round(avg or 0.0, 2))
        return ApiResponse.success(data={'promedio': promedio})


class ResenaResponderView(generics.UpdateAPIView):
    queryset = Resena.objects.all()
    serializer_class = ResenaResponderSerializer
    permission_classes = (IsAdministrador,)

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ApiResponse.success(data=serializer.data, message='Respuesta registrada')


class ResenaModerarView(generics.UpdateAPIView):
    queryset = Resena.objects.all()
    serializer_class = ResenaModerarSerializer
    permission_classes = (IsAdministrador,)

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ApiResponse.success(data=serializer.data, message='Estado de moderación actualizado')
