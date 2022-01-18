from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import datetime
import sys
from settings import MAN, WOMAN


def create_connection_vk(token, user_token):
    vk_longpoll = vk_api.VkApi(token=token)
    try:
        longpoll = VkLongPoll(vk_longpoll)
    except vk_api.exceptions.ApiError:
        print('Вы ввели неверный групповой токен. Перезапустите программу и введите корректный ключ доступа.')
        sys.exit()
    vk = VkBot(token, user_token)
    try:
        vk.get_list_photo(1)
    except vk_api.exceptions.ApiError:
        print('Вы ввели неверный групповой токен. Перезапустите программу и введите корректный ключ доступа.')
        sys.exit()
    print('Токены успешно прошли проверку валидности! Бот запущен, можно начинать работу в Вк.')


class VkBot:

    def __init__(self, token_group, token_user):
        self.vk = vk_api.VkApi(token=token_group)
        self.vk_user = vk_api.VkApi(token=token_user)
        self.keyboard = VkKeyboard()
        self.keyboard.add_button('Найди мне пару', color=VkKeyboardColor.PRIMARY)
        self.keyboard.add_button('Найди пару другому пользователю', color=VkKeyboardColor.PRIMARY)

    def write_msg(self, user_id, message, data_photo=None):
        self.vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),
                                    'keyboard': self.keyboard.get_keyboard(), 'attachment': data_photo})

    def get_name(self, user_id):
        data = self.vk.method('users.get', {'user_ids': user_id})
        return f'{data[0]["first_name"]}'

    def get_data_user(self, user_id):
        data = self.vk.method('users.get', {'user_ids': user_id, 'fields': 'city, sex, bdate'})
        # if 'bdate' not in data[0] or 'city' not in data[0] or 'sex' not in data[0]:
        #     return False, False, False
        if 'bdate' not in data[0]:
            bdate = False
        else:
            bdate = data[0]['bdate']
        if 'city' not in data[0]:
            city = False
        else:
            city = data[0]['city']['id']
        if 'sex' not in data[0]:
            sex = False
        else:
            sex = data[0]['sex']
        # return data[0]['bdate'], data[0]['city']['id'], data[0]['sex']
        return bdate, city, sex

    def get_list_users(self, city, sex, age):
        data = self.vk_user.method('users.search', {'city': city, 'fields': 'relation, city', 'count': 1000, 'sex': sex,
                                               'age_from': age - 3, 'age_to': age + 3})
        for i in data['items']:
            if ('relation' in i and i['relation'] in (6, 1)) and ('city' in i and i['city']['id'] == city):
                yield i['id']

    def get_age(self, data):
        try:
            date_obj = datetime.datetime.strptime(data, '%d.%m.%Y')
        except (ValueError, TypeError):
            return False
        delta = datetime.datetime.now() - date_obj
        delta = delta.days / 365.2425
        return int(delta)

    def check_sex(self, sex):
        if sex == MAN:
            sex = WOMAN
        else:
            sex = MAN
        return sex

    def get_list_photo(self, id):
        result = self.vk_user.method('photos.get', {'owner_id': id, 'album_id': 'profile', 'extended': 1})
        return result

    def get_user_json(self, user_id):
        data = self.vk.method('users.get', {'user_ids': user_id, 'fields': 'city, sex, relation, bdate'})
        return data

    def get_photo(self, result):
        list_photo = []

        for i in result['items']:
            likes = i['likes']['count']
            likes += i['comments']['count']
            list_photo.append([likes, i['id']])

        list_photo.sort(key=lambda x: x[0])
        for i in list_photo:
            del i[0]
        new_list = [item for sublist in list_photo[-3:] for item in sublist]
        return new_list

    def send_response_three(self, event, i, id_photo):
        self.write_msg(event.user_id, f'Будет исполнено) Ссылка на страницу пользователя - vk.com/id{i},'
                                 f' наслаждайтесь)', data_photo=f'photo{i}_{id_photo[0]},photo{i}_{id_photo[1]},'
                                                                f'photo{i}_{id_photo[2]}')

    def send_response_two(self, event, i, id_photo):
        self.write_msg(event.user_id, f'Будет исполнено) Ссылка на страницу пользователя - vk.com/id{i},'
                                    ' наслаждайтесь)', data_photo=f'photo{i}_{id_photo[0]},photo{i}_{id_photo[1]}')

    def send_response_one(self, event, i, id_photo):
        self.write_msg(event.user_id, f'Будет исполнено) Ссылка на страницу пользователя - vk.com/id{i},'
                                    f' наслаждайтесь)', data_photo=f'photo{i}_{id_photo[0]}')
