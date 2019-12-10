# -*- coding: utf-8 -*-

import http.client
import json
import urllib.parse

conn = http.client.HTTPSConnection("api.hh.ru")
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
headers = {'Content-type': 'application/json','User-Agent': user_agent}

def get_vacancies(search_value):
    text_value = urllib.parse.quote_plus(search_value)
    conn.request('GET', '/vacancies?text={}'.format(text_value), None, headers)
    response = conn.getresponse()
    body = response.read().decode()
    print(body)
    return json.loads(body)


def test_items_on_page_count():


def test_inc():
    assert get_vacancies() == 4

if __name__ == "__main__":
    vacs = get_vacancies()
    print("pages:", vacs["pages"])
    print("per page", vacs["per_page"])
    print("page:", vacs["page"])
    print("total found", vacs["found"])
    print(len(vacs["items"]))
