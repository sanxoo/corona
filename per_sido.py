import datetime
import pathlib
import csv

from prefect import task, flow

import openapi
import storage

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
def collect(date=None):
    date = date or (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    path = fetch(date)
    save(path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        sys.stderr.write(f"\nusage: {sys.argv[0]} YYYYmmdd\n\n")
        sys.exit()
    date = sys.argv[1]
    collect(date)

