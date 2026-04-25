"""Notes app views."""

from rest_framework import viewsets
from .models import Note
from .serializers import NoteSerializer
# Test Auto Deploy! 🚀


class NoteViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Notes.

    list:      GET    /api/notes/
    create:    POST   /api/notes/
    retrieve:  GET    /api/notes/{id}/
    update:    PUT    /api/notes/{id}/
    partial:   PATCH  /api/notes/{id}/
    destroy:   DELETE /api/notes/{id}/
    """

    queryset = Note.objects.all()
    serializer_class = NoteSerializer
