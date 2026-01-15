import os
import time
from datetime import datetime
from threading import Thread

import requests
import json


class Busses(Thread):
    def __init__(self):
        super().__init__()
        self.busses = {}
        self.bids = {}
        self.new_data = False
        self.new_bid_data = False
        self.load_existing_data()
        self.go = True
        self.last_update = datetime.utcnow()

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
            'displayRows': 500,
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
            'proximityWithinDistance': '500',
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

    def update_bid_data(self, bus_id, bus_data):
        price = bus_data.get('currentBid', 0.0)
        if bus_id not in self.bids:
            self.bids[bus_id] = []
            self.new_bid_data = True
        last_price = 0.0
        for bid in self.bids[bus_id]:
            bid_price = bid.get('price', 0.0)
            if bid_price > last_price:
                last_price = bid_price
        if price > last_price:
            bid_entry = {
                'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'price': price,
            }
            self.bids[bus_id].append(bid_entry)
            self.new_bid_data = True
            if bus_id in self.busses:
                self.busses[bus_id]['currentBid'] = price
                self.new_data = True

    def get_bus_details(self, bus_id):
        account_id, asset_id = self.bus_id_to_asset_id(bus_id)
        import requests

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
            'x-api-correlation-id': '33c4b02b-45f2-40a4-bc32-cd014af712ec',
            'x-api-key': 'af93060f-337e-428c-87b8-c74b5837d6cd',
            'x-ecom-session-id': '6ae3cc40-e5ed-46df-ad27-9370bd3ff651',
            'x-page-unique-id': 'aHR0cHM6Ly93d3cuZ292ZGVhbHMuY29tL2VuL2Fzc2V0LzEyMi81MDA4',
            'x-referer': 'https://www.govdeals.com/en/asset/122/5008',
            'x-user-id': '-1',
            'x-user-timezone': 'America/New_York',
        }

        json_data = {
            'businessId': 'GD',
            'siteId': 1,
        }

        response = requests.post(f'https://maestro.lqdt1.com/assets/{asset_id}/{account_id}/false', headers=headers,
                                 json=json_data)
        data = response.json()
        new_asset_id = data.get('assetId')
        new_account_id = data.get('accountId')
        new_bus_id = self.bus_id_from_asset_id(new_account_id, new_asset_id)
        if new_bus_id == bus_id:
            self.busses[bus_id].update(data)
            self.new_data = True
        return data

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
        else:
            self.busses = {}
        if os.path.exists('data/bids.json'):
            with open('data/bids.json', 'r', encoding='utf-8') as f:
                self.bids = json.load(f)
        else:
            self.bids = {}

    def save_data(self):
        if self.new_data:
            if os.path.exists('data/busses.json'):
                current_date = datetime.now()
                os.rename('data/busses.json', f'data/busses_{current_date.strftime("%Y%m%d_%H%M%S")}.json')
            with open('data/busses.json', 'w', encoding='utf-8') as f:
                json.dump(self.busses, f, ensure_ascii=False, indent=4)
            self.new_data = False
        if self.new_bid_data:
            if os.path.exists('data/bids.json'):
                current_date = datetime.now()
                os.rename('data/bids.json', f'data/bids_{current_date.strftime("%Y%m%d_%H%M%S")}.json')
            with open('data/bids.json', 'w', encoding='utf-8') as f:
                json.dump(self.bids, f, ensure_ascii=False, indent=4)
            self.new_bid_data = False

    def reload(self):
        new_busses = self.get_new_busses()
        for bus_id in new_busses:
            bus = new_busses[bus_id]
            self.update_bid_data(bus_id, bus)
            if bus_id not in self.busses:
                print(f"New bus found: {bus_id}")
                self.busses[bus_id] = bus
                self.new_data = True
        self.save_data()

    def update(self):
        for bus_id in self.busses:
            updated_bus = self.update_bus(bus_id)
            self.busses[bus_id] = updated_bus
        self.save_data()

    def update_bus(self, bus_id):
        bus = self.busses[bus_id]
        if not bus.get('assetLongDesc', False) and not bus.get('hidden', False):
            print(f"Updating bus ID: {bus_id}")
            self.get_bus_details(bus_id)
        auction_end_time = bus.get('assetAuctionEndDateUtc')
        time_left = datetime.strptime(auction_end_time, '%Y-%m-%dT%H:%M:%SZ') - datetime.utcnow()
        if time_left.total_seconds() <= 0:
            bus['isSoldAuction'] = True
        time_left_formatted = str(time_left)
        bus['timeRemaining'] = time_left_formatted
        return bus

    def hide_bus(self, bus):
        if bus in self.busses:
            self.busses[bus]['hidden'] = True
            self.new_data = True
            self.save_data()

    def run(self):
        while self.go:
            now = datetime.utcnow()
            if (now - self.last_update).total_seconds() > 300:
                print(f"Automatic update of bus data... {now.isoformat()}")
                self.update()
                self.last_update = now
            time.sleep(.5)


if __name__ == '__main__':
    b = Busses()
    b.reload()
