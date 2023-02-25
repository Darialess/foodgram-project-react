

from rest_framework import mixins, viewsets


class GetPostMixin(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    pass


class ListPostDelPatch(mixins.CreateModelMixin,
                       mixins.ListModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.UpdateModelMixin):
    pass


class ListPostDel(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    pass

