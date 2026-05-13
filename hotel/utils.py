from rest_framework.response import Response
from rest_framework import status

class ApiResponse:
    """
    Estructura estandarizada para todas las respuestas de la API.
    Coincide con la interfaz del Frontend:
    {
        "code": "status_code",
        "message": "Mensaje descriptivo",
        "data": { ... }
    }
    """
    @staticmethod
    def success(data=None, message="Operación exitosa", status_code=status.HTTP_200_OK):
        return Response({
            "code": str(status_code),
            "message": message,
            "data": data
        }, status=status_code)

    @staticmethod
    def error(message="Ha ocurrido un error", data=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response({
            "code": str(status_code),
            "message": message,
            "data": data
        }, status=status_code)
