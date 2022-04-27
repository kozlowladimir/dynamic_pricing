from collections import defaultdict
import numpy as np


class Hotel:
    """
    Класс, описыающие состояние отеля
    """
    def __init__(self, number_of_rooms=15, number_of_days=365):
        """
        Инициализация. Задание свойств отеля
        :param number_of_rooms: число номеров
        :param number_of_days: число дней для симуляции
        """
        self.number_of_rooms = number_of_rooms
        self.number_of_days = number_of_days
        self.state = np.zeros([self.number_of_rooms, self.number_of_days])
        self.cancel_days = defaultdict(list)
        self.bookings = defaultdict(dict)  # day -> {uid --> data}

    def is_vacant(self, request):
        """
        Проверка, есть ли свободные места для данного запроса
        :param request: запрос
        :return: номера свободных комнат
        """
        nights = self.state[:, request.start_day: request.end_day + 1]
        indices = []
        for idx, row in enumerate(nights):
            if sum(row) == 0:
                indices.append(idx)
        if len(indices) >= request.persons:
            return indices
        else:
            return []

    def booking(self, request, rooms, id, price):
        """
        Бронирование заказа
        :param request: заказ
        :param rooms: комнаты
        :param id: номер заказа
        :param price: цена бронирования
        :return: None
        """
        for k in range(request.persons):
            self.state[rooms[k], request.start_day: request.end_day + 1] = id

        # регистрируем дату отмены
        if request.cancellation_day is not None:
            self.cancel_days[request.cancellation_day].append(
                (id, rooms[0:request.persons], request.start_day, request.end_day))

        # добавляем в список заказов
        self.bookings[request.start_day][id] = {'price_per_person': price, 'request': request}

    def get_loading(self, days):
        """
        Загрузка отеля
        :param days: интересующий день (или дни)
        :return: число занятых номеров
        """
        if days >= self.number_of_days:
            return 0

        return np.count_nonzero(self.state[:, days], axis=0)

    def cancel_request(self, day):
        """
        Регистрируем отмену брони
        :param day: день отмены
        :return: None
        """
        for data in self.cancel_days[day]:
            id, rooms, start_day, end_day = data
            for room in rooms:
                self.state[room, start_day: end_day + 1] = 0

            self.bookings[start_day].pop(id)

    def get_revenue(self, day):
        """
        Получаем выручку за указанный день
        :param day: интересующий день
        :return: выручка
        """
        revenue = 0
        for id in self.bookings[day]:
            revenue += self.bookings[day][id]['price_per_person'] * self.bookings[day][id]['request'].persons
        return revenue
