import sys
sys.path.append('D:/git/dynamic_pricing/')


import numpy as np
from tqdm import tqdm

from app.utils.acceptance_rule import AcceptanceRule
from app.utils.event_generator import EventGenerator
from app.utils.hotel import Hotel
from app.utils.pricing import PricingDefault


def simulate(verbose=0):
    """
    Симуляция деятельности отеля
    :return: общая выручка
    """
    number_of_days = 365
    nominal_price = 1000
    mu = 30

    event = EventGenerator(mu=mu)
    hotel = Hotel(number_of_days=number_of_days)
    acceptance = AcceptanceRule(nominal_price=nominal_price)
    pricing = PricingDefault(1000)

    total_revenue = 0
    uid = 1
    for day in range(number_of_days):
        # print(f"day simulate: {day}")
        requests = event.generate_requests()

        for request in requests:
            request.fill(day)
            # проверяем, есть ли места
            vacant_rooms = hotel.is_vacant(request)
            if len(vacant_rooms):

                # устанавливаем цену
                price = pricing.set_price(hotel, request)

                # проверяем, устраивает ли цена
                acceptance_result = acceptance.decision(price)
                if acceptance_result:
                    hotel.booking(request, vacant_rooms, uid, price)
                if verbose:
                    print(f'price: {price}')
                    print(f'LoS: {request.LoS}')
                    print(f'depth: {request.depth}')
                    print(f'acceptance_result: {acceptance_result}')
                    print(f'vacant_rooms: {vacant_rooms}')
                    print(f'person: {request.persons}')

            uid += 1
            if verbose:
                print('----------------')

        # удаляем отменённые заказы
        hotel.cancel_request(day)

        # считаем выручку за день. Деньги за всех гостей за всё время проживания поступают сразу в день заезда
        revenue = hotel.get_revenue(day)
        total_revenue += revenue

    return total_revenue, pricing, (hotel.state == 0).sum() / hotel.number_of_rooms / number_of_days

print('begin')

if __name__ == '__main__':

    # Симулируем N_sim раз и считаем среднюю выручку и её дисперсию при заданной стратегии
    # 1000

    res = []
    range_N = 1
    threshold = 1
    hotel_states = []
    for k in tqdm(range(range_N)):
        total_revenue, pricing, hotel_state = simulate()
        res.append(total_revenue)
        hotel_states.append(hotel_state)

    print({
            "range": range_N,
            "revenue_mean": round(np.mean(res), 0),
            "revenue_std": round(np.std(res), 0),
            "hotel_states_mean": round(np.mean(hotel_states), 4),
            "hotel_states_std": round(np.std(hotel_states), 4),
    })

    with open('./app/logs/file.txt', 'w') as f:
        f.write('base_experiments\n')
        f.write(f'threshold: {threshold}\n')
        f.write(f'range_N: {range_N}\n')
        f.write(f'revenue_mean: {round(np.mean(res), 0)}\n')
        f.write(f'revenue_std: {round(np.std(res), 0)}\n')
        f.write(f'hotel_states_mean: {round(np.mean(hotel_states), 4)}\n')
        f.write(f'hotel_states_std: {round(np.std(hotel_states), 4)}\n')
