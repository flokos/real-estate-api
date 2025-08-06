from rest_framework import viewsets, permissions
from ..permissions import IsOwnerOrAdminOrReadOnly
from ..models import Property
from ..serializers.property import PropertySerializer
from ..mixins import LoggingMixin

class PropertyViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnly]