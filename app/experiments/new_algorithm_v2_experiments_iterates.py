import argparse
from datetime import datetime
import sys
sys.path.append('D:/git/dynamic_pricing/')

import numpy as np
from tqdm import tqdm

from app.utils.acceptance_rule import AcceptanceRule
from app.utils.event_generator import EventGenerator
from app.utils.hotel import Hotel
from app.utils.pricing import PricingSomeMethodv2, PricingSomeMethodv3, PricingSomeMethodv4


def simulate(params, pricing_strategy='PricingSomeMethodv2', verbose=0):
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
    if pricing_strategy == 'PricingSomeMethodv2':
        pricing = PricingSomeMethodv2(1000, **params)
    elif pricing_strategy == 'PricingSomeMethodv3':
        pricing = PricingSomeMethodv3(1000, **params)
    elif pricing_strategy == 'PricingSomeMethodv4':
        pricing = PricingSomeMethodv4(1000, **params)

    total_revenue = 0
    uid = 1
    for day in range(number_of_days):
        acc_count = {}
        requests = event.generate_requests()
        total_requests_per_day_count = 0
        for request in requests:
            request.fill(day)
            # проверяем, есть ли места
            vacant_rooms = hotel.is_vacant(request)
            if len(vacant_rooms):

                # устанавливаем цену
                price = pricing.set_price(hotel, request, total_requests_per_day_count, verbose=verbose)

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
                pricing.update_history({'price': price, 'acceptance': acceptance_result})
                if not acc_count.get(request.depth):
                    acc_count[request.depth] = 1
                else:
                    acc_count[request.depth] += 1

            uid += 1
            total_requests_per_day_count += 1
            if verbose:
                print('----------------')

        # удаляем отменённые заказы
        hotel.cancel_request(day)
        pricing.update_queue(acc_count)

        # считаем выручку за день. Деньги за всех гостей за всё время проживания поступают сразу в день заезда
        revenue = hotel.get_revenue(day)
        total_revenue += revenue

    return total_revenue, pricing, (hotel.state == 0).sum() / hotel.number_of_rooms / number_of_days


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--iter_count', required=True)
    parser.add_argument('--explore_count', required=True)
    parser.add_argument('--pricing_strategy', required=True)
    args = parser.parse_args()

    range_N = int(args.iter_count)
    explore_count = int(args.explore_count)
    pricing_strategy = args.pricing_strategy

    # Симулируем N_sim раз и считаем среднюю выручку и её дисперсию при заданной стратегии
    # 1000
    thresholds = [1.0, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8, 3, 3.2, 3.4, 3.6, 3.8, 4]

    for threshold in thresholds:
        res = []
        hotel_states = []
        time_begin = datetime.now()
        for k in tqdm(range(range_N)):
            total_revenue, pricing, hotel_state = simulate({'threshold': threshold, 'explore_count': explore_count})
            res.append(total_revenue)
            hotel_states.append(hotel_state)

        time_diff = (datetime.now() - time_begin).total_seconds()

        file_path = './app/logs/'
        file_name = f'{pricing_strategy}_algorithm.txt'
        with open(file_path + file_name, 'a') as f:
            f.write(f'{pricing_strategy}\n')
            f.write(f'threshold: {threshold}\n')
            f.write(f'iter_counts: {range_N}\n')
            f.write(f'explore_count: {explore_count}\n')
            f.write(f'revenue_mean: {round(np.mean(res), 0)}\n')
            f.write(f'revenue_std: {round(np.std(res), 0)}\n')
            f.write(f'hotel_states_mean: {round(np.mean(hotel_states), 4)}\n')
            f.write(f'hotel_states_std: {round(np.std(hotel_states), 4)}\n')
            f.write(f'time per loop, s: {round(time_diff / range_N, 2)}\n')
            f.write('\n')
            f.write('\n')
