from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from ..models import Resena, Estadia


class ResenaListSerializer(serializers.ModelSerializer):
    huesped_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Resena
        fields = (
            'id',
            'huesped_nombre',
            'calificacion',
            'comentario',
            'fecha_creacion',
            'respuesta_administrador',
            'es_inapropiada',
        )

    def get_huesped_nombre(self, obj):
        try:
            h = obj.estadia.reserva.huesped
            return f"{h.nombre} {h.apellido}"
        except Exception:
            return ''


class ResenaCreateSerializer(serializers.ModelSerializer):
    estadia = serializers.PrimaryKeyRelatedField(queryset=Estadia.objects.all())

    class Meta:
        model = Resena
        fields = ('id', 'estadia', 'calificacion', 'comentario')

    def validate_calificacion(self, value):
        if not (1 <= int(value) <= 5):
            raise serializers.ValidationError('La calificación debe estar entre 1 y 5')
        return int(value)

    def validate_estadia(self, value):
        estadia = value

        if not estadia.fecha_checkout:
            raise PermissionDenied('La estadía no está cerrada (sin fecha de checkout)')
        if getattr(estadia.reserva, 'estado', None) != 'COMPLETADA':
            raise PermissionDenied('La reserva asociada no está COMPLETADA')

        if hasattr(estadia, 'resena'):
            raise serializers.ValidationError('Ya existe una reseña para esta estadía')

        return value

    def create(self, validated_data):
        return super().create(validated_data)


class ResenaResponderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resena
        fields = ('respuesta_administrador',)


class ResenaModerarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resena
        fields = ('es_inapropiada',)
