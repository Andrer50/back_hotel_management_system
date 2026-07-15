from django.urls import path
from .views import (
    ResenaListCreateView,
    ResenaPromedioView,
    ResenaResponderView,
    ResenaModerarView,
)

urlpatterns = [
    path('resenas', ResenaListCreateView.as_view(), name='resena-list-create'),
    path('resenas/promedio', ResenaPromedioView.as_view(), name='resena-promedio'),
    path('resenas/<int:pk>/responder', ResenaResponderView.as_view(), name='resena-responder'),
    path('resenas/<int:pk>/moderar', ResenaModerarView.as_view(), name='resena-moderar'),
]
