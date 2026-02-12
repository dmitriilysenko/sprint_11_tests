import pytest 
from time import sleep

def one_more(x):
    return x + 1


def get_sort_list(str):
    new_list = sorted(str.split(', '))
    return new_list


@pytest.mark.parametrize(
    'input_arg, expected_result',  # Названия аргументов, передаваемых в тест.
    [(4, 5), (3, 4)]  # Список кортежей со значениями аргументов.
)
def test_one_more(input_arg, expected_result):  # Те же параметры, что и в декораторе.
    assert one_more(input_arg) == expected_result


def test_sort():
    """Тестируем функцию get_sort_list()."""
    result = get_sort_list('Яша, Саша, Маша, Даша')
    assert result == ['Даша', 'Маша', 'Саша', 'Яша']


@pytest.mark.slow  # Отмечаем маркером тест.
def test_type():
    """Тестируем тип данных, возвращаемых из get_sort_list()."""
    sleep(3)
    result = get_sort_list('Яша, Саша, Маша, Даша')
    # Провальный тест:
    # ожидаем число, но вернётся список.
    assert isinstance(result, list)


def cartesian_product(a, b):
    return a * b


@pytest.mark.parametrize('x', [1, 2])
@pytest.mark.parametrize('y', ['one', 'two'])
def test_cartesian_product(x, y):
    assert cartesian_product(x, y) is not None