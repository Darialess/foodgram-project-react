from io import StringIO

DATA = {
    'ingredient__name': 'Название ингредиента',
    'amount_sum': 'Количество',
    'ingredient__measurement_unit': 'Единица измерения'
}


def make_send_file(ingredient):

    shop_list_file = StringIO()
    shop_list_file.write('Список ингредиентов:\n\n')

    for i in ingredient:
        for key, value in i.items():
            shop_list_file.write(f'{DATA[key]} - {value}\n')
            if key == 'amount_sum':
                shop_list_file.write('\n')

    return shop_list_file