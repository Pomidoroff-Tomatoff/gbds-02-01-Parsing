import requests
from lxml import html


def duplicate_remover_0(values: list = None) -> list:
    ''' Удаляем дубликаты слов в оригинальном(!) списке,
        Адрес оригинального (полученного) списка возвращается.
        Порядок слов исходный (не меняется).
        Прим.: Цикл for не используем, так как он пересчитывает условие проверки цикла
               только в самом начале, а в процессе работы -- нет!
    '''
    if type(values) is list:
        i = 0
        while i < len(values)-1:  # Цикл for не пересчитывает условие проверки цикла и поэтому не используется
            # print(f"{i=}")
            j = i + 1
            while j < len(values):
                # print(f"{j = }")
                if values[i] == values[j]:
                    # print(f"pop {j}")
                    values.pop(j)
                else:
                    j += 1
            else:
                i += 1
    return values


def duplicate_remover_1(values: list = None) -> list:
    ''' Удаляем дубликаты слов в оригинальном(!) списке,
        Адрес оригинального (полученного) списка возвращается.
        Порядок слов исходный (не меняется).
        ПРИМЕЧАНИЕ: Значение i+1 в срезе values[i + 1::] может выйти за границы,
        но это не приводит к ошибке!
    '''
    if type(values) is list:
        i = 0
        while i < len(values)-1:
            while values[i] in values[i+1::]:
                values.pop(values.index(values[i], i+1, ))
            else:
                i += 1
    return values


def duplicate_remover_2(values: list = None) -> list:
    ''' Удаляем дубликаты слов в оригинальном(!) списке,
        но всё равно возвращаем адрес полученного списка.
        Порядок слов исходный (не меняется).
        ПРИМЕЧАНИЕ: Значение i+1 в срезе values[i + 1::] может выйти за границы,
        но это не приводит к ошибке!
    '''
    if type(values) is list:
        i = 0
        while i < len(values)-1:
            while values[i+1::].count(values[i]):
                values.pop(values.index(values[i], i+1))
            else:
                i += 1
    return values

def duplicate_remover_2B(values: list = None) -> list:
    ''' Удаляем дубликаты слов в оригинальном(!) списке,
        но всё равно возвращаем адрес полученного списка.
        Порядок слов исходный (не меняется).
        ЭТО НЕ РАБОТАЕТ -- видимо на срезе
    '''
    if type(values) is list:
        i = 0
        while i < len(values)-1:
            while values[i+1::].count(values[i]):
                values[i+1::].remove(values[i])
            else:
                i += 1
    return values


def duplicate_remover_3(values: list = None) -> list:
    ''' Удаляем дубликаты слов в списке
        -- без изменения оригинального списка
        -- возвращаем новый список
        -- порядок слов нарушается (почти всегда)
    '''
    if type(values) is list:
        if len(values) > 1:
            values_clear = list(set(values))
        else:
            values_clear = values.copy()
    else:
        values_clear = values
    return values_clear

'''
url = 'https://nahabino.hh.ru/vacancy/73197298'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
}
response = requests.get(url=url, headers=headers)
dom = html.fromstring(response.text)

duplicate_remover = duplicate_remover_0

values_dup = dom.xpath('//a[@data-qa="vacancy-company-name"]//text()')
print(f"{values_dup}")
values_res = duplicate_remover(values_dup)

print(f"{values_res}")
print(f"\n")
print(f"{duplicate_remover(['',])=}")
print(f"{duplicate_remover([])=}")
'''

a='123'
duplicate_remover = duplicate_remover_2B
print(f"{duplicate_remover([a, a, a, a, a, a, ])=}")