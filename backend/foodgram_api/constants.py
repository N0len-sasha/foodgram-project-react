MAX_USER_CHARACTERS = 150
MAX_EMAIL_CHARACTERS = 256
MIN_INGREDIENT_VALUE = 1
MAX_INGREDIENT_VALUE = 32767
MIN_COOKING_VALUE = 1
MAX_COOKING_VALUE = 10080
MAX_NAME_LENGH = 200
INGREDIENT_VALIDATION_MESSAGE = ('Ингредиентов должно быть'
                                 f'{MIN_INGREDIENT_VALUE} или более')
MAX_INGREDIENT_VALIDATION_MESSAGE = ('Ингредиентов должно быть'
                                     f'не больше {MAX_INGREDIENT_VALUE}')
COOKING_VALIDATION_MESSAGE = ('Время приготовления должно'
                              f'быть не менее {MIN_COOKING_VALUE} минуты')
MAX_COOKING_VALIDATION_MESSAGE = ('Время приготовления должно'
                                  f'быть более {MAX_COOKING_VALUE} минут')
