class Request:
    """
    класс, описивающий свойства запроса на бронирование
    """

    def __init__(self, LoS=None, persons=None, depth=None, cancellation=None):
        """
        :param LoS: продолжительность заказа
        :param persons: число гостей
        :param depth: глубина бронирования
        :param cancellation: глубина отмены бронирования
        """
        self.LoS = LoS
        self.persons = persons
        self.depth = depth
        self.cancellation_day = cancellation

    def __repr__(self):
        return f"""
          LoS: {self.LoS}\n
          persons: {self.persons}\n
          depth: {self.depth}\n
          cancellation_day: {self.cancellation_day}
          """

    def fill(self, day):
        """
        переводит данные запроса на конкретный день.
        :param day: номер дня, в который приходит запрос
        :return: None
        """
        self.start_day = self.depth + day
        self.end_day = self.start_day + self.LoS
        self.booking_day = day

        if self.cancellation_day is not None:
            self.cancellation_day = self.start_day - self.cancellation_day
