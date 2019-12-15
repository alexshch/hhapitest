# -*- coding: utf-8 -*-

import http.client
import json
import random
import string
import urllib.parse

conn = http.client.HTTPSConnection("api.hh.ru")
headers = {'Content-type': 'application/json', 'User-Agent': 'Mozilla/5.0'}

def get_vacancies(search_text):
    return send_request('GET', search_text, headers)

def post_vacancies(search_text):
    return send_request('POST', search_text, headers)

def put_vacancies(search_text):
    return send_request('PUT', search_text, headers)

def send_request(method, search_text, request_headers):
    search_text = urllib.parse.quote_plus(search_text)
    conn.request(method, '/vacancies?text={}'.format(search_text), None, request_headers)
    response = conn.getresponse()
    response_body = response.read().decode()
    return response.status, response_body

def get_vacancies_by_id(id):
    conn.request('GET', '/vacancies/{}'.format(id), None, headers)
    response = conn.getresponse()
    response_body = response.read().decode()
    return response.status, response_body

def random_string(stringLength=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))


# позитивные тесты
# разные позитивные тесты
def test_positive_tram_ru():
    status, body = get_vacancies('трамвай')
    assert status == 200
    vacations = json.loads(body)
    assert vacations['found'] > 0
    assert len(vacations['items']) > 0

def test_positive_tram_jp():
    status, body = get_vacancies('路面電車')
    assert status == 200
    vacations = json.loads(body)
    assert vacations['found'] == 0
    assert len(vacations['items']) == 0

def test_positive_tram_en():
    status, body = get_vacancies('trips')
    assert status == 200
    vacations = json.loads(body)
    assert vacations['found'] > 0
    assert len(vacations['items']) > 0

# тесты поисковых опероторов
def test_get_taxi_not_driver():
    status, body = get_vacancies('такси NOT водитель')
    search_str = 'такси'
    should_not_be = 'водитель'
    assert status == 200
    vacations = json.loads(body)
    assert vacations['found'] > 0
    assert len(vacations['items']) > 0
    # проверим первую страницу поисковой выгрузки по наименованию вакансии и описанию
    for vac in vacations['items']:
        name_contain = search_str in str.lower(vac['name'])
        name_not_contain = not should_not_be in str.lower(vac['name'])
        status, body = get_vacancies_by_id(vac['id'])
        assert status == 200
        full_vacancy = json.loads(body)
        desc_contain = search_str in str.lower(full_vacancy['description'])
        desc_not_contain = not should_not_be in str.lower(full_vacancy['description'])
        assert name_contain or desc_contain
        assert name_not_contain and desc_not_contain

# тесты поисковых опероторов
def test_get_java_and_python_and_cpp():
    status, body = get_vacancies('java AND python AND c++')
    assert status == 200
    vacations = json.loads(body)
    assert vacations['found'] > 0
    assert len(vacations['items']) > 0

# негативные тесты
# граничные значения 256 KB -- max
def test_negative_too_long_url():
    str = random_string(102144)
    status, _ = get_vacancies(str)
    assert status == 414

def test_negative_bad_gateway():
    str = random_string(51072)
    status, _ = get_vacancies(str)
    assert status == 502

def test_post_vacancies():
    status, _ = post_vacancies('трамвай')
    assert status == 403

def test_put_vacancies():
    status, _ = put_vacancies('трамвай')
    assert status == 405

def test_get_vacancies_no_user_agent_header():
    status, _ = send_request('GET', 'трамвай', {'Content-type': 'application/json'})
    assert status == 400


# тесты на безопастность sql, html, js, xss

def test_sql_injection_1():
    status, body = get_vacancies("'driver'''''''''''''UNION SELECT '2'")
    assert status == 200
    vacations = json.loads(body)
    assert vacations['found'] == 0
    assert len(vacations['items']) == 0

def test_sql_injection_2():
    status, body = get_vacancies("driver' AND id IS NULL; --")
    assert status == 200
    vacations = json.loads(body)
    assert vacations['found'] == 0
    assert len(vacations['items']) == 0

def test_xss_injectiob():
    xss_injection_str = (
        '&#X3c;',
        '&#X03c;',
        '&#X003c;',
        '&#X0003c;',
        '&#X00003c;',
        '&#X000003c;',
        '<SCRIPT SRC="http://ha.ckers.org/xss.jpg"></SCRIPT>',
        """<!--#exec cmd="/bin/echo '<SCR'"--><!--#exec cmd="/bin/echo 'IPT SRC=http://ha.ckers.org/xss.js></SCRIPT>'"-->""",
        "<? echo('<SCR)';",
        """echo('IPT>alert("XSS")</SCRIPT>'); ?>"""
    )
    for injection in xss_injection_str:
        status, body = get_vacancies(injection)
        assert status == 200
        vacations = json.loads(body)
        assert vacations['found'] == 0
        assert len(vacations['items']) == 0


if __name__ == "__main__":
   pass
