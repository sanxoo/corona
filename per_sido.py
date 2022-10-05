import datetime
import pathlib
import csv

from prefect import task, flow

import openapi
import storage
import db

@task
def target_dates():
    date = datetime.date.today() - datetime.timedelta(days=1)
    if 4 < date.weekday(): return []
    holidays = []
    service_url = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getAnniversaryInfo"
    i, m = (date.year, date.month)
    for year, month in [(i, m), (i - 1, 12) if m == 1 else (i, m - 1)]:
        items = openapi.fetch(service_url, {"solYear": f"{year}", "solMonth": f"{month:02}"})
        holidays += [i["locdate"] for i in items if i["isHoliday"] == "Y"]
    dstr = date.strftime("%Y%m%d")
    if dstr in holidays: return []
    dist = [dstr]
    while 1:
        date = date - datetime.timedelta(days=1)
        dstr = date.strftime("%Y%m%d")
        if dstr not in holidays: break
        if date.weekday() < 5: break
        dist.append(dstr)
    return dist

@task(retries=2, retry_delay_seconds=600)
def fetch(date):
    service_url = "http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson"
    items = openapi.fetch(service_url, {"startCreateDt": date, "endCreateDt": date})
    if not items: raise Exception(f"no items for {date}")
    path = pathlib.Path("/home/emma/tmp") / f"{pathlib.Path(__file__).stem}_{date}.csv"
    with open(path, "w") as f:
        writer = csv.DictWriter(f, fieldnames=items[0].keys())
        writer.writeheader()
        writer.writerows(items)
    return path

@task
def save_to_storage(path):
    storage.put("corona", path)

@task
def save_to_db(path):
    columns = ["stdDay", "gubun", "defCnt", "deathCnt", "incDec", "localOccCnt", "overFlowCnt", "qurRate"]
    list_of_dict = []
    with open(path) as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            d = {k: (v == "-" and "0" or v) for k, v in zip(header, row) if k in columns}
            d["stdDay"] = datetime.datetime.strptime(d["stdDay"], "%Y년 %m월 %d일 %H시").date()
            list_of_dict.append(d)
    db.insert("corona_per_sido", list_of_dict)

@flow(name="collect corona per sido")
def collect(dates):
    dates = dates or target_dates()
    for date in dates:
        path = fetch(date)
        save_to_storage(path)
        save_to_db(path)
        path.unlink()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        sys.stderr.write(f"\nusage: {sys.argv[0]} YYYYmmdd [YYYYmmdd +]\n\n")
        sys.exit()
    collect(sys.argv[1:])

