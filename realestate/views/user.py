from rest_framework import viewsets
from ..models import User
from ..serializers.user import UserSerializer
from ..permissions import IsAdminOrReadOnly, IsOwnerOrAdminOrReadOnly
from ..mixins import LoggingMixin

class UserViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_permissions(self):
        if self.action in ["retrieve", "update", "partial_update"]:
            return [IsOwnerOrAdminOrReadOnly()]
        return [permission() for permission in self.permission_classes]