import re

from collections import Counter
from datetime import datetime


def counter(list):
    top_five_list = []
    for _, count in Counter(list).most_common(5):
        top_five_list.append(count)
    return top_five_list


request_pattern = re.compile(
    r'^\[(?P<request_date>[\d]{1,2}\/[\w]+\/[\d]{4}'
    r'\s[\d]{1,2}:[\d]{1,2}:[\d]{1,2})]\s'
    r'\"(?P<request_type>[\w]+)\s((?P<protocol>https?)(://)(?P<url>[^\?\s]+))'
)
file_extension_pattern = re.compile(r'\.(?P<file_extension>[a-z]+)$')
time_ms_pattern = re.compile(r'\s(?P<time_ms>[\d]+$)')
www_pattern = re.compile(r'https?://www\.')


def datetime_format(data_i_vremya):
    datetime_object = datetime.strptime(data_i_vremya, '%d/%b/%Y %H:%M:%S')
    return datetime_object


def parse(
    ignore_files=False,
    ignore_urls: list = None,
    start_at=None,
    stop_at=None,
    request_type: str = None,
    ignore_www=False,
    slow_queries=False
):
    urls = []
    queries_dict = {}
    with open('log.log') as file:
        for line in file:
            request_log = request_pattern.search(line)
            if request_log:
                request_date = request_log.group('request_date')
                request_type_ = request_log.group('request_type')
                url = request_log.group('url')
                www_check = (request_log.group('protocol')
                             + request_log.group(5) + url
                             )
                file_extension = file_extension_pattern.search(url)
                if ignore_files:
                    if file_extension:
                        continue
                if ignore_urls:
                    if url in ignore_urls:
                        continue
                if ignore_www:
                    if www_pattern.search(www_check):
                        url = url.replace('www.', '')
                if request_type:
                    if request_type != request_type_:
                        continue
                if start_at:
                    if (datetime_format(start_at) > datetime_format(request_date)):
                        continue
                if stop_at:
                    if (datetime_format(stop_at) < datetime_format(request_date)):
                        continue
                if slow_queries:
                    time_request = time_ms_pattern.search(line)
                    if time_request:
                        time_ms = int(time_request.group('time_ms'))
                        if queries_dict.get(url):
                            queries_dict[url] += time_ms
                        else:
                            queries_dict[url] = time_ms
                urls.append(url)
    if slow_queries:
        for url, count in Counter(urls).items():
            queries_dict[url] //= count
        return sorted(queries_dict.values(), reverse=True)[:5]
    return counter(urls)


def main():
    parse()


if __name__ == '__main__':
    main()
