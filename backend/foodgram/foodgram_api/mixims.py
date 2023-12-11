from rest_framework import mixins, viewsets
from users.validators import validator_username


class ValidationMixin:
    def validate_username(self, value):
        return validator_username(value)


class GetObjectMixim(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    pass
