import requests
from datetime import datetime, timedelta
import pandas as pd
import re
import io
import os
from tqdm import tqdm
import time


now = datetime.now()


def get_data(year, month, day):
    url = "http://spaceweather.rra.go.kr/data/models/SELAB/ASSA_FLARE/"

    url = url + year + "/" + month + "/" + day + "/" + "ASSA_Spot_flare_" + year + month + day + "00.txt"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(
            url,
            headers = headers,
        )
    except:
        response = pd.DataFrame()
        response.status_code = 502

    return response


def refine_data(process_day, response):
    regex = re.compile(r'(?P<year>\d{4}).*(?P<time>\d{4}).*\s.*\s(?P<assa>(.|\n)*)')
    matchobj = regex.search(response)
    time = matchobj.group("time")
    assa = matchobj.group("assa")
    try:
        data = pd.read_csv(io.StringIO(assa), names=['ASSA', 'coord', 'C', 'M', 'R'], header=None, sep=',')
    except:
        data = pd.DataFrame(columns=['ASSA', 'coord', 'C', 'M', 'R'])
    data.insert(0, "time", time)
    data.insert(0, "date", process_day.strftime("%Y-%m-%d"))
    data.drop(['coord'], axis=1, inplace=True)
    data = data[:-1]
    
    return data


def createDirectory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Failed to create the directory.")


if __name__=="__main__":
    folder = "data"
    filename = "result.csv"

    createDirectory(folder)

    response = pd.DataFrame()
    response.status_code = 200

    # 중간부터 시작하는 경우
    # now = datetime(2022,2,1)

    process_day = now
    data = pd.DataFrame(columns=['ASSA', 'coord', 'C', 'M', 'R'])

    # if result file is not
    data.to_csv(folder+"/"+filename, sep=" ", index=False)

    with tqdm() as pbar:
        while 1:
            year = format(process_day.year, '04')
            month = format(process_day.month, '02')
            day = format(process_day.day, '02')
            
            response = get_data(
                year,
                month,
                day,
            )

            if response.status_code == 502:
                pass
            elif response.status_code == 404:
                f = open(folder+"/except.txt", 'a')
                f.write(process_day.strftime("%Y-%m-%d") + " 0000\n")
                f.close()

            else:
                data = refine_data(process_day, response.content.decode('utf-8'))
                data.to_csv(
                    folder+"/"+filename,
                    sep = " ",
                    header = False,
                    mode = "a",
                    index = False,
                )       

            process_day = process_day - timedelta(days=1)
            time.sleep(1)
            pbar.update(1)


    print(data)
