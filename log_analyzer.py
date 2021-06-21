import argparse
import json
import re
from collections import defaultdict
from collections import Counter

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='file', action='store', default=None)
args = parser.parse_args()

request_dict = defaultdict(lambda: {"GET": 0, "POST": 0, "PUT": 0, "DELETE": 0, "HEAD": 0, "COUNT": 0, "DURATION": 0})
methods_count_dict = defaultdict(int)
requests_count_dict = defaultdict(int)

final_dict = []
final_dict_400 = []

with open(args.file) as file:
    for index, line in enumerate(file.readlines()):
        if index > 250:
            break
        try:
            ip = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line).group()
            method = re.search(r"(POST|GET|PUT|DELETE|HEAD)", line).group()
            url = re.search(r"(POST|GET|PUT|DELETE|HEAD) (.+) HTTP", line).group(2)
            status_code = re.search(r"\" (\d{3}) \d", line).group(1)
            duration = re.search(r"\d (\d{4}) \"", line).group(1)
        except AttributeError:
            pass
        # request_dict[ip][method] += 1
        # request_dict[ip]["COUNT"] += 1
        requests_count_dict[ip] += 1
        methods_count_dict[method] += 1

        if re.findall(r"4\d\d", status_code):
            final_dict_400.append((ip, method, url, status_code, duration))
        else:
            final_dict.append(
                {"IP": ip, "METHOD": method, "URL": url, "STATUS_CODE": status_code, "DURATION": duration})
long_request_list = sorted(final_dict, key=lambda duration: duration['DURATION'], reverse=True)
count_request_dict = {k: v for k, v in sorted(requests_count_dict.items(), key=lambda item: item[1], reverse=True)}
top_long = long_request_list[:10]
top_count = {k: count_request_dict[k] for k in list(count_request_dict)[:10]}

# print(final_dict_400)

print("Кол-во запросов по адресам:" + json.dumps(requests_count_dict, indent=4))
print("Кол-во запросов по методам:" + json.dumps(methods_count_dict, indent=4))
print("Топ 10 запросов с которых были сделаны запросы:" + json.dumps(top_count, indent=4))
print("Топ 10  самых долгих запросов:" + json.dumps(top_long, indent=4))
