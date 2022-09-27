import datetime
import pathlib
import csv

from prefect import task, flow

import openapi
import storage
import db

def default_date():
    return datetime.date.today().strftime("%Y%m%d")

@task(retries=3, retry_delay_seconds=10)
def fetch(date):
    service_url = "http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson"
    items = openapi.fetch(service_url, date, date)
    if not items: raise Exception(f"no items for {date}")
    path = pathlib.Path("/home/emma/tmp") / f"{pathlib.Path(__file__).stem}_{date}.csv"
    with open(path, "w") as f:
        writer = csv.DictWriter(f, fieldnames=items[0].keys())
        writer.writeheader()
        writer.writerows(items)
    return path

@task
def save(path):
    storage.put("corona", path)
    path.unlink()

@flow(name="collect corona per sido")
def collect(date):
    date = date or default_date()
    path = fetch(date)
    save(path)

@task
def download_file(date):
    path = pathlib.Path("/home/emma/tmp") / f"{pathlib.Path(__file__).stem}_{date}.csv"
    storage.get("corona", path)
    return path

@task
def record(path):
    columns = ["stdDay", "gubun", "defCnt", "deathCnt", "incDec", "localOccCnt", "overFlowCnt", "qurRate"]
    list_of_dict = []
    with open(path) as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            d = {k: v for k, v in zip(header, row) if k in columns}
            d["stdDay"] = datetime.datetime.strptime(d["stdDay"], "%Y년 %m월 %d일 %H시").date()
            list_of_dict.append(d)
    db.insert("corona_per_sido", list_of_dict)
    path.unlink()

@flow(name="load corona per sido")
def load(date):
    date = date or default_date()
    path = download_file(date)
    record(path)

if __name__ == "__main__":
    funcs = {
        "collect": collect, "load": load
    }
    import sys
    if len(sys.argv) != 3:
        sys.stderr.write(f"\nusage: {sys.argv[0]} {'|'.join(funcs.keys())} YYYYmmdd\n\n")
        sys.exit()
    funcs[sys.argv[1]](sys.argv[2])

