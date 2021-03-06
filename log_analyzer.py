import argparse
import json
import re
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='file', action='store', default=None)
args = parser.parse_args()

request_dict = defaultdict(lambda: {"GET": 0, "POST": 0, "PUT": 0, "DELETE": 0, "HEAD": 0, "COUNT": 0, "DURATION": 0})
methods_count_dict = defaultdict(int)
requests_count_dict = defaultdict(int)
count_400_dict = defaultdict(int)
count_500_dict = defaultdict(int)

final_dict = []
final_dict_400 = []
final_dict_500 = []

with open(args.file) as file:
    for index, line in enumerate(file.readlines()):
        try:
            ip = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line).group()
            method = re.search(r"(POST|GET|PUT|DELETE|HEAD)", line).group()
            url = re.search(r"(POST|GET|PUT|DELETE|HEAD) (.+) HTTP", line).group(2)
            status_code = re.search(r"\" (\d{3}) \d", line).group(1)
            duration = re.search(r"\d (\d{4}) \"", line).group(1)
        except AttributeError:
            pass
        requests_count_dict[ip] += 1
        methods_count_dict[method] += 1
        if re.findall(r"4\d\d", status_code):
            count_400_dict[ip] += 1
        if re.findall(r"5\d\d", status_code):
            count_500_dict[ip] += 1
        final_dict.append(
            {"IP": ip, "METHOD": method, "URL": url, "STATUS_CODE": status_code, "DURATION": duration})

long_request_list = sorted(final_dict, key=lambda duration: duration['DURATION'], reverse=True)
count_request_dict = {k: v for k, v in sorted(requests_count_dict.items(), key=lambda item: item[1], reverse=True)}
top_long = long_request_list[:10]
top_count = {k: count_request_dict[k] for k in list(count_request_dict)[:10]}
top_400 = sorted(count_400_dict.items(), key=lambda count: count[1], reverse=True)[:10]
top_500 = sorted(count_500_dict.items(), key=lambda count: count[1], reverse=True)[:10]

for i in range(len(top_400)):
    for el in final_dict:
        if (el["IP"] == top_400[i][0]) and el["STATUS_CODE"].startswith('4'):
            el.pop("DURATION")
            el["COUNT"] = top_400[i][1]
            final_dict_400.append(el)
            break

for i in range(len(top_500)):
    for el in final_dict:
        if (el["IP"] == top_500[i][0]) and el["STATUS_CODE"].startswith('5'):
            el.pop("DURATION")
            el["COUNT"] = top_500[i][1]
            final_dict_500.append(el)
            break

result_dict = {
    "?????????? ??????-???? ????????????????": str(index),
    "??????-???? ???????????????? ???? ??????????????:": requests_count_dict,
    "??????-???? ???????????????? ???? ??????????????:": methods_count_dict,
    "?????? 10 ???????????????? ?? ?????????????? ???????? ?????????????? ??????????????:": top_count,
    "?????? 10  ?????????? ???????????? ????????????????:": top_long,
    "?????? 10 ???????????? ?? ???????????????????? ??????????????:": final_dict_400,
    "?????? 10 ???????????? ?? ?????????????????? ??????????????:": final_dict_500
}

with open("./result.json", "w") as f:
    s = json.dumps(result_dict, indent=4)
    f.write(s)
