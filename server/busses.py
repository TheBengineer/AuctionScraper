import os
import time
from datetime import datetime
from threading import Thread

import requests
import json

from tqdm import tqdm

BUS_POLL_INTERVAL = 3600  # seconds


class Busses(Thread):
    def __init__(self, stop_event=None):
        super().__init__()
        self.daemon = True
        self.busses = {}
        self.bids = {}
        self.new_data = False
        self.new_bid_data = False
        self.load_existing_data()
        self.stop_event = stop_event
        self.last_update = datetime.utcnow()
        self.session = requests.Session()
        self.headers = {}

    def setup_session(self):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0aGViZW5naW5lZXIiLCJqdGkiOiI0NmQ5ZDY1My1kZjVjLTQ5NzMtODE3YS01MTFkMjZiOGQxMWYiLCJ1c2VyX2lkIjoiMzczOTIzOCIsInVzZXJfZm5hbWUiOiJCZW4iLCJ1c2VyX2xuYW1lIjoiaG9sbGVyYW4iLCJ1c2VyX2VtYWlsIjoiYmVuZ2luZWVyaW5nZWxtQGdtYWlsLmNvbSIsInVzZXJfcGJfbGV2ZWwiOiIxIiwidXNlcl9wYl9sZXZlbF9kdCI6IjAxLzExLzIwMjYgMDA6MDA6MDAuMDAwIiwiZW1fdG9rZW4iOiJlZTUzMTU1NDBkMGIxNGZkZWNmOGJmNzcwZTFlMjQzOTE5YmMyZWZiYjRkODI1ODQ2NiEiLCJpcF9hZGRyZXNzIjoiOjpmZmZmOjE2OS4yNTQuMTI5LjEiLCJ1c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0My4wLjAuMCBTYWZhcmkvNTM3LjM2IiwibmJmIjoxNzY4NTk3NjEzLCJleHAiOjE3Njg2MDEyMTMsImlzcyI6IldlYkFwaS5BdXRoZW50aWNhdGlvbiIsImF1ZCI6IkVjb20ifQ.wc1AKWQO49xFl4w-86B0KPH5DBqvoxHg1lKl1NtSiMw',
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
            'x-api-correlation-id': 'ad6305a3-dbe6-40df-ae66-18183c80a783',
            'x-api-key': 'af93060f-337e-428c-87b8-c74b5837d6cd',
            'x-ecom-session-id': 'a034f0a9-7dfe-4498-acba-1983b42ce3e7',
            'x-page-unique-id': 'aHR0cHM6Ly93d3cuZ292ZGVhbHMuY29tL2VuL2Fzc2V0LzI0NS8yNjIxNA=',
            'x-referer': 'https://www.govdeals.com/en/asset/245/26214',
            'x-user-id': '3739238',
            'x-user-timezone': 'America/New_York',
        }
        self.headers.update(headers)
        self.session.headers.update(headers)
        self.session.get('https://www.govdeals.com/')

    def get_new_busses(self):
        for cookie in self.session.cookies:
            self.headers[cookie.name] = cookie.value

        json_data = {
            'categoryIds': '6',
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
            'proximityWithinDistance': '700',
        }

        response = self.session.post('https://maestro.lqdt1.com/search/list', headers=self.headers, json=json_data)
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

        json_data = {
            'businessId': 'GD',
            'siteId': 1,
        }

        response = self.session.post(f'https://maestro.lqdt1.com/assets/{asset_id}/{account_id}/false',
                                     headers=self.headers,
                                     json=json_data)
        data = response.json()
        new_asset_id = data.get('assetId')
        new_account_id = data.get('accountId')
        new_bus_id = self.bus_id_from_asset_id(new_account_id, new_asset_id)
        if new_bus_id == bus_id:
            for key, value in data.items():
                if value is not None:
                    self.busses[bus_id][key] = value
            self.new_data = True
        return data

    def get_bus_bids(self, bus_id):
        account_id, asset_id = self.bus_id_to_asset_id(bus_id)

        json_data = {
            'auctionId': 1,
            'page': 1,
            'displayRows': 50,
        }

        response = self.session.post(f'https://maestro.lqdt1.com/assets/{asset_id}/{account_id}/bids/search',
                                     headers=self.headers,
                                     json=json_data)
        data = response.json()
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
        print("Saving bus data...")
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
        for bus_id in tqdm(self.busses.keys()):
            updated_bus = self.update_bus(bus_id)
            self.busses[bus_id] = updated_bus
        self.save_data()

    def update_bids(self):
        for bus_id in tqdm(self.busses.keys()):
            bus = self.busses[bus_id]
            last_bid_update = bus.get('lastBidUpdate', '1970-01-01T00:00:00Z')
            last_bid_update_dt = datetime.strptime(last_bid_update, '%Y-%m-%dT%H:%M:%SZ')
            time_since_last_update = datetime.utcnow() - last_bid_update_dt
            try:
                if int(bus.get('modelYear', 0)) > 2010:
                    bus["hidden"] = True
            except Exception:
                pass
            if time_since_last_update.total_seconds() < BUS_POLL_INTERVAL:
                continue
            if bus.get('assetLongDesc', False) and not bus.get('hidden', False):
                bus_bids = self.get_bus_bids(bus_id)
                existing_bids = {bid.get("price"): bid for bid in self.bids.get(bus_id, [])}
                for new_bid in bus_bids:
                    new_bid_price = new_bid.get('bidAmount', 0.0)
                    if bus_id not in self.bids:
                        self.bids[bus_id] = []
                        self.new_bid_data = True
                    if new_bid_price not in existing_bids:
                        bid_entry = {
                            'timestamp': new_bid.get('bidDateTime', datetime.utcnow()),
                            'buyerId': new_bid.get('buyerId'),
                            'price': new_bid_price,
                        }
                        self.bids[bus_id].append(bid_entry)
                        self.new_bid_data = True
                existing_bids = {bid.get("price"): bid for bid in self.bids.get(bus_id, [])}
                highest_bid = max(existing_bids.keys())
                bus['lastBidUpdate'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                bus['currentBid'] = highest_bid
                self.new_data = True
                self.update_bid_data(bus_id, bus)
        self.save_data()

    def update_bus(self, bus_id):
        bus = self.busses[bus_id]
        if not bus.get('assetLongDesc', False) and not bus.get('hidden', False):
            print(f"Updating bus ID: {bus_id}")
            bus['assetLongDesc'] = "loading"
            self.get_bus_details(bus_id)
        auction_end_time = bus.get('assetAuctionEndDateUtc')
        if auction_end_time:
            time_left = datetime.strptime(auction_end_time, '%Y-%m-%dT%H:%M:%SZ') - datetime.utcnow()
            if time_left.total_seconds() <= 0:
                bus['isSoldAuction'] = True
            time_left_formatted = str(time_left)
            bus['timeRemaining'] = time_left_formatted
        if not bus.get('latitude', True):
            del bus['latitude']
            self.new_data = True
        if not bus.get('longitude', True):
            del bus['longitude']
            self.new_data = True
        return bus

    def hide_bus(self, bus):
        if bus in self.busses:
            self.busses[bus]['hidden'] = True
            self.new_data = True
            self.save_data()

    def add_lot(self, lot_id):
        if lot_id not in self.busses:
            self.busses[lot_id] = {}
            self.get_bus_details(lot_id)
            return True
        return False

    def bidders(self):
        bidders = {}
        print("Mapping bidders...")
        for bus_id in tqdm(self.busses.keys()):
            for bid in self.bids.get(bus_id, []):
                bidder = bid.get('buyerId')
                if bidder:
                    if bidder not in bidders:
                        bidders[bidder] = []
                    bidders[bidder].append(bus_id)
        graph = {"nodes": [], "links": [], "details": {}}
        bus_ids = set()
        bidder_ids = set()
        for bidder, buses in bidders.items():
            bidder_ids.add(bidder)
            for bus_id in buses:
                bus_ids.add(bus_id)
                graph['links'].append({'source': bidder, 'target': bus_id})
        for bus_id in tqdm(self.busses.keys()):
            hidden = self.busses[bus_id].get('hidden', False)
            if not hidden:
                bus_ids.add(bus_id)
        for bus_id in bus_ids:
            graph['nodes'].append({'id': bus_id, 'group': 'bus'})
            graph['details'][bus_id] = self.busses.get(bus_id, {})
        for bidder in bidder_ids:
            graph['nodes'].append({'id': bidder, 'group': 'bidder'})
        return graph

    def run(self):
        print("Busses thread started...")
        self.setup_session()
        while not self.stop_event.is_set():
            now = datetime.utcnow()
            if (now - self.last_update).total_seconds() > BUS_POLL_INTERVAL:
                print(f"Automatic update of bus data... {now.isoformat()}")
                self.update()
                self.last_update = now
                self.update_bids()
            time.sleep(.5)
        print("Busses thread stopping...")


if __name__ == '__main__':
    b = Busses()
    b.reload()
