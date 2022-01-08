import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from DB import select_data, insert_data
from bot_func import VkBot
import sys


# with open('t.txt') as f:
#     token = f.read().strip()
#
# with open('toc_vk.txt') as f:
#     user_token = f.read().strip()

token = input('Введите групповой токен Вк:\n')
user_token = input('Введите пользовательский токен Вк:\n')

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

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()

        if request == "привет":
            name = vk.get_name(event.user_id)
            vk.write_msg(event.user_id, f"Хай, {name}")
        elif request == "найди мне пару":
            list_id_users = select_data(event.user_id)
            new_list = [item for sublist in list_id_users for item in sublist]
            data, city, sex = vk.get_data_user(event.user_id)
            sex = vk.check_sex(sex)
            age = vk.get_age(data)
            for i in vk.get_list_users(city, sex, age):
                if i in new_list:
                    continue
                list_id_photo = vk.get_list_photo(i)
                id_photo = vk.get_photo(list_id_photo)
                if len(id_photo) == 3:
                    vk.send_response_three(event, i, id_photo)
                    data_user = vk_longpoll.method('users.get', {'user_ids': i})
                    insert_data(i, data_user, event.user_id)
                elif len(id_photo) == 2:
                    vk.send_response_two(event, i, id_photo)
                    data_user = vk_longpoll.method('users.get', {'user_ids': i})
                    insert_data(i, data_user, event.user_id)
                elif len(id_photo) == 1:
                    vk.send_response_one(event, i, id_photo)
                    data_user = vk_longpoll.method('users.get', {'user_ids': i})
                    insert_data(i, data_user, event.user_id)
                break
        elif request == 'найди пару другому пользователю':
            end = False
            search_data_user = []
            vk.write_msg(event.user_id, 'Введите ID пользователя, для которого хотите подыскать пару (только цифры).')
            for event_two in longpoll.listen():
                if event_two.type == VkEventType.MESSAGE_NEW and event_two.to_me:
                    vk_id = event_two.text
                    try:
                        vk_id = int(vk_id)
                        user_json = vk.get_user_json(vk_id)
                    except ValueError:
                        vk.write_msg(event.user_id, 'Нужно ввести только цифры. Будьте внимательнее :)')
                        end = True
                        break
                    search_data_user = vk_longpoll.method('users.get', {'user_ids': vk_id})
                    break
            if end:
                continue
            elif not search_data_user:
                vk.write_msg(event.user_id, 'Пользователя с указанным ID не существует, попробуйте еще раз.')
            elif 'deactivated' in user_json[0]:
                vk.write_msg(event.user_id, 'Страница указанного Вами пользователя удалена/отключена.')
            else:
                list_id_users = select_data(vk_id)
                new_list = [item for sublist in list_id_users for item in sublist]
                data, city, sex = vk.get_data_user(vk_id)
                if not data:
                    vk.write_msg(event.user_id, 'У пользователя на странице не указаны/скрыты дата или город, в связи с '
                                             'этим подбор пары невозможен.')
                    continue
                sex = vk.check_sex(sex)
                age = vk.get_age(data)
                if not age:
                    vk.write_msg(event.user_id, 'У указанного Вами пользователя дата рождения либо целиком не указана, либо'
                                             ' не указан год рождения, в связи с этим невозможно произвести подбор с '
                                             'учетом возраста.')
                    continue
                for i in vk.get_list_users(city, sex, age):
                    if i in new_list:
                        continue
                    list_id_photo = vk.get_list_photo(i)
                    id_photo = vk.get_photo(list_id_photo)
                    if len(id_photo) == 3:
                        vk.send_response_three(event, i, id_photo)
                        data_user = vk_longpoll.method('users.get', {'user_ids': i})
                        insert_data(i, data_user, vk_id)
                    elif len(id_photo) == 2:
                        vk.send_response_two(event, i, id_photo)
                        data_user = vk_longpoll.method('users.get', {'user_ids': i})
                        insert_data(i, data_user, vk_id)
                    elif len(id_photo) == 1:
                        vk.send_response_one(event, i, id_photo)
                        data_user = vk_longpoll.method('users.get', {'user_ids': i})
                        insert_data(i, data_user, vk_id)
                    break
        else:
            vk.write_msg(event.user_id, "Не понял вашего ответа...")
