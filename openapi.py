import xml.etree.ElementTree
import requests

def parse_items(text):
    items = []
    for item in xml.etree.ElementTree.fromstring(text).iterfind("body/items/item"):
        items.append({e.tag:e.text for e in item})
    return items

def parse_total(text):
    return int(xml.etree.ElementTree.fromstring(text).find("body/totalCount").text)

def fetch(service_url, start_date, end_date):
    params = {
        "ServiceKey": "rp+Ayp72Chlp0fJBzQrSYtINgORq+xn1G4LmyMTsnEFIZaolXfueTakbBm1wXbYj9g8z17Dm7owJ9kxn4jIuSQ==",
        "pageNo": 1,
        "numOfRows": 10,
        "startCreateDt": start_date,
        "endCreateDt": end_date
    }
    res = requests.get(service_url, params=params)
    items = parse_items(res.text)
    total = parse_total(res.text)
    while len(items) < total:
        params["pageNo"] += 1
        res = requests.get(service_url, params=params)
        items += parse_items(res.text)
    return items

