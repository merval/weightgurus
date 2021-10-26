#!/usr/bin/env python3
from datetime import datetime

import requests
import json


def transform_weight(weight):
    """
    Transforms normal weight in pounds to Weight Gurus format

    :param weight: Weight in pounds
    :return: Weight Guru format
    """
    try:
        weight = str(weight).replace('.', '')
        transformed_weight = int(weight)
        return transformed_weight
    except ValueError:
        try:
            transformed_weight = int(float(weight))
            return transformed_weight
        except ValueError:
            print(f"Caught ValueError! '{weight}' is not a number.")


class WeightGurus:

    def __init__(self, username, password):
        self.login_data = {
            'email': username,
            'password': password,
            'web': True
        }
        self.headers = None
        self.start_date = 'start=1970-01-01T01:00:00.504Z'
        self.weight_history = None
        self.add_weight = {}

    def __do_login(self):
        req = requests.post('https://api.weightgurus.com/v3/account/login', data=self.login_data)
        try:
            json_data = req.json()
            self.headers = {'authorization': f"Bearer {json_data['accessToken']}"
                            }
        except Exception as e:
            print(f"Caught Exception reading JSON: {e}")

    def __get_weight_history(self, start_date=None):
        if start_date:
            self.start_date = f"start={start_date}"
        req = requests.get(f'https://api.weightgurus.com/v3/operation/?{self.start_date}', headers=self.headers)
        try:
            json_data = req.json()
        except Exception as e:
            print(f"Caught Exception reading JSON: {e}")
            json_data = None
        return json_data

    def get_all(self):
        self.__do_login()
        return json.dumps(self.__get_weight_history(), indent=4, sort_keys=True)

    def get_since_date(self, start_date):
        self.__do_login()
        return json.dumps(self.__get_weight_history(start_date), indent=4, sort_keys=True)

    def get_latest(self):
        self.__do_login()
        weight_data = self.__get_weight_history()
        return json.dumps(weight_data['operations'][-1])

    def manual_entry(self, weight, bmi=None, body_fat=None, muscle_mass=None, water=None):
        """
        Weight Gurus has a weird way of adding weight, they want integer values (numbers) without decimals.
        This requires you to take you weight and remove the decimal. So, 100.0 pounds would be 1000 when you add it.
        """
        self.__do_login()
        self.headers['user-agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, ' \
                                     'like Gecko) Chrome/89.0.4389.128 Safari/537.36'
        self.headers['content-type'] = 'application/json'
        if bmi:
            self.add_weight['bmi'] = int(bmi)
        if body_fat:
            self.add_weight['bodyFat'] = int(body_fat)
        self.add_weight['entryTimestamp'] = str(datetime.now())
        if muscle_mass:
            self.add_weight['muscleMass'] = int(muscle_mass)
        self.add_weight['operationType'] = 'create'
        self.add_weight['source'] = 'manual'
        if water:
            self.add_weight['water'] = int(water)
        if weight is None:
            print("You need to provide your weight")
            exit(1)
            return False
        weight = transform_weight(weight)
        self.add_weight['weight'] = weight
        req = requests.post('https://api.weightgurus.com/v3/operation',
                            data=json.dumps(self.add_weight),
                            headers=self.headers)
        status_code = req.status_code
        if status_code == 201:
            print("Successfully added weight!")
            return req.json()


if __name__ == "__main__":
    weight_gurus = WeightGurus('username', 'password')
    weight_gurus.get_all()
