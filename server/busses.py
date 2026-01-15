import os
from datetime import datetime

import requests
import json


class Busses:
    def __init__(self):
        self.busses = {}
        self.load_existing_data()

    def get_new_busses(self):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': 'cf620d1d8f904b5797507dc5fd1fdb80',
            'Origin': 'https://www.govdeals.com',
            'Referer': 'https://www.govdeals.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'x-api-correlation-id': '9d46e865-d398-4fea-9540-33f9a9306a45',
            'x-api-key': 'af93060f-337e-428c-87b8-c74b5837d6cd',
            'x-ecom-session-id': 'dd57d677-7d4c-4bef-818b-0a6bde3cd1e6',
            'x-page-unique-id': 'aHR0cHM6Ly93d3cuZ292ZGVhbHMuY29tL2VuL3NlYXJjaD9rV29yZD1idXMmemlwY29kZT0zMDU3NyZtaWxlcz0yNTAmcG49MSZwcz0xMjA',
            'x-referer': 'https://www.govdeals.com/en/search?kWord=bus&zipcode=30577&miles=250&pn=1&ps=120',
            'x-user-id': '-1',
            'x-user-timezone': 'America/New_York',
        }

        json_data = {
            'categoryIds': '',
            'businessId': 'GD',
            'searchText': 'bus',
            'isQAL': False,
            'locationId': None,
            'model': '',
            'makebrand': '',
            'auctionTypeId': None,
            'page': 1,
            'displayRows': 120,
            'sortField': 'bestfit',
            'sortOrder': 'desc',
            'sessionId': 'bcf4bb67-90f0-4ee7-868d-ed5ce0150989',
            'requestType': 'search',
            'responseStyle': 'productsOnly',
            'facets': [
                'categoryName',
                'auctionTypeID',
                'condition',
                'saleEventName',
                'sellerDisplayName',
                'product_pricecents',
                'isReserveMet',
                'hasBuyNowPrice',
                'isReserveNotMet',
                'sellerType',
                'warehouseId',
                'region',
                'currencyTypeCode',
                'countryDesc',
                'tierId',
            ],
            'facetsFilter': [],
            'timeType': '',
            'sellerTypeId': None,
            'accountIds': [],
            'zipcode': '30577',
            'proximityWithinDistance': '250',
        }

        response = requests.post('https://maestro.lqdt1.com/search/list', headers=headers, json=json_data)
        data = response.json()
        busses = {}
        for bus in data.get('assetSearchResults', []):
            account_id = bus.get('accountId')
            asset_id = bus.get('assetId')
            bus_id = self.bus_id_from_asset_id(account_id, asset_id)
            busses[bus_id] = bus
        return busses

    @staticmethod
    def bus_id_to_asset_id(bus_id):
        account_id, asset_id = bus_id.split('-')
        return account_id, asset_id

    @staticmethod
    def bus_id_from_asset_id(account_id, asset_id):
        return f"{account_id}-{asset_id}"

    def load_existing_data(self, ):
        if os.path.exists('data/busses.json'):
            with open('data/busses.json', 'r', encoding='utf-8') as f:
                self.busses = json.load(f)
                return
        print("No existing busses.json file found. Starting fresh.")
        self.busses = {}

    def save_data(self):
        if os.path.exists('data/busses.json'):
            current_date = datetime.now()
            os.rename('data/busses.json', f'busses_{current_date.strftime("%Y%m%d_%H%M%S")}.json')
        with open('data/busses.json', 'w', encoding='utf-8') as f:
            json.dump(self.busses, f, ensure_ascii=False, indent=4)

    def scan_bus(self, bus):
        return bus

    def reload(self):
        new_busses = self.get_new_busses()
        for bus_id in new_busses:
            bus = new_busses[bus_id]
            if bus_id not in self.busses:
                print(f"New bus found: {bus.get('title')} (ID: {bus_id})")
                scanned_bus = self.scan_bus(bus)
                self.busses[bus_id] = scanned_bus
        self.save_data()

    def update(self):
        for bus_id in self.busses:
            updated_bus = self.update_bus(bus_id)
            self.busses[bus_id] = updated_bus

    def update_bus(self, bus_id):
        bus = self.busses[bus_id]
        auction_end_time = bus.get('assetAuctionEndDateUtc')
        time_left = datetime.strptime(auction_end_time, '%Y-%m-%dT%H:%M:%SZ') - datetime.utcnow()
        if time_left.total_seconds() <= 0:
            bus['isSoldAuction'] = True
        time_left_formatted = str(time_left)
        bus['timeRemaining'] = time_left_formatted
        return bus


if __name__ == '__main__':
    b = Busses()
    b.reload()
