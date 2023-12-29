from users.validators import validator_username


class ValidationMixin:
    def validate_username(self, value):
        return validator_username(value)
