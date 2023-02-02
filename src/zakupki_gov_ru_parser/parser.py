import asyncio
import json
import re
import shelve
import urllib
import pandas as pd
import requests
from bs4 import BeautifulSoup

from .consts import BASE_LINK, BASE_QUERY_PARAMS
from .settings import settings
from .utils import get_request, headers


def _load_companies_csv(path: str, target_col_name: str = "Наименование") -> set:
    companies_data = pd.read_csv(path)
    companies = set(companies_data[target_col_name])
    return companies


def get_registry_links(raw_html: bytes) -> list[str]:
    soup = BeautifulSoup(raw_html, features="html.parser")

    regestry_entries_tag = soup.find_all("div", {"class": "registry-entry__header-mid__number"})
    regestry_links = [
        f"{BASE_LINK}{tag.find('a', {'target': '_blank'}).attrs['href']}"
        for tag in regestry_entries_tag
    ]

    return regestry_links


# "fz44": "on",
# "fz223": "on",
async def parse_company_purchases(company: str, parameter: str):
    query_params = {**BASE_QUERY_PARAMS, **{"searchString": company}}

    params_kit = [{**query_params, **{f"{parameter}": "on"}}]

    link = f"{BASE_LINK}/epz/order/extendedsearch/results.html"

    resps = await asyncio.gather(
        *(get_request(link, query_params=params) for params in params_kit)
    )

    # 0_links - fz44, 1_links - fz223
    links = [get_registry_links(resp.content) for resp in resps]
    return links


async def purchases_fz223_parser(company: str):
    parameter = "fz223"
    temp = await parse_company_purchases(company, parameter)
    return temp


# pydantic models
async def purchases_fz44_parser(company: str):
    parameter = "fz44"
    temp = await parse_company_purchases(company, parameter)
    return temp


async def parse_resource():
    companies = _load_companies_csv(settings.companies_list)
    dict_links = {}
    while companies:
        target_company = companies.pop()
        # fz223

        temp = await purchases_fz223_parser(target_company)
        dict_links[target_company] = temp
        print(dict_links)
        await get_company_fz223_links(dict_links)
        dict_links = {}

        # fz44
        # temp = await purchases_fz44_parser(target_company)
        # dict_links[target_company] = temp
        # print(dict_links)
        # await get_company_fz44_links(dict_links)
        # dict_links = {}


# for fz223 84 - 155 lines
async def get_company_fz223_links(dict_company):
    for key, value in dict_company.items():
        for item in value:
            if not item:
                continue
            else:
                for i in item:
                    if not i:
                        continue
                    else:
                        get_company_fz223_info(i, key)


def get_company_fz223_info(link, company):
    req = requests.get(link, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    company_info_fz223 = {
        company: {
            "number": None,
            "status": None,
            "purchase_method": None,
            "customer_inn": None,
            "executor_inn": None,
            "start_price": None,
            "documents": False,
            "comment": None,
            "purchase_link": None,
            "document_link": None,
            "document_format": None,
            "winner_price": None
        }
    }

    number = soup.find("div", class_="registry-entry__header-mid__number")
    status = soup.find("div", class_="registry-entry__header-mid__title")
    purchase = soup.find("div", class_="col-9 mr-auto").find_next().find_next().find_next().find_next().find_next() \
        .find_next().find_next()
    inn = soup.find("div", class_="ml-1 common-text__value")
    start_price = soup.find("div", class_="price-block__value")
    documents = 1 if check_documents_fz223(link) else 0

    company_info_fz223[company]['number'] = number.text.strip()
    company_info_fz223[company]['status'] = status.text.strip() if status is not None else None
    company_info_fz223[company]['purchase_method'] = purchase.text.strip()
    company_info_fz223[company]['customer_inn'] = inn.text.strip()
    company_info_fz223[company]['start_price'] = start_price.text.strip().replace("\xa0", ' ') if start_price is not \
                                                                                                  None else None

    company_info_fz223[company]['documents'] = documents
    company_info_fz223[company]['purchase_link'] = link
    company_info_fz223[company]['document_link'] = get_document_fz223(link)
    company_info_fz223[company]['document_format'] = get_type_document_fz223(link)

    print(company_info_fz223)


def check_documents_fz223_link(url):
    link_id = re.findall(r'\d+', url)
    return f"https://zakupki.gov.ru/epz/order/notice/notice223/documents.html?noticeInfoId={link_id[-1]}"


def check_documents_fz223(url):
    temp_link = check_documents_fz223_link(url)
    req = requests.get(temp_link, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    title = soup.find("div", class_="attachment__value")
    return title


# for fz44

async def get_company_fz44_links(dict_company):
    for key, value in dict_company.items():
        for item in value:
            if not item:
                continue
            else:
                for i in item:
                    if not i:
                        continue
                    else:
                        pass
                        get_company_fz44_info(i, key)


def get_company_fz44_info(link, company):
    req = requests.get(link, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    company_info_fz44 = {
        company: {
            "number": None,
            "status": None,
            "purchase_method": None,
            "customer_inn": None,
            "executor_inn": None,
            "start_price": None,
            "documents": False,
            "comment": None,
            "purchase_link": None,
            "document_link": None,
            "document_format": None,
            "winner_price": None
        }
    }

    number = soup.find("span", class_="cardMainInfo__purchaseLink distancedText").find_next()
    status = soup.find("span", class_="cardMainInfo__state distancedText")
    purchase = soup.find("span", class_="section__info")
    inn = find_inn_fz44(link)
    start_price = soup.find("span", class_="cardMainInfo__content cost")

    company_info_fz44[company]['number'] = number.text.strip()
    company_info_fz44[company]['status'] = status.text.strip()
    company_info_fz44[company]['purchase_method'] = purchase.text.strip()
    company_info_fz44[company]['customer_inn'] = inn
    company_info_fz44[company]['start_price'] = start_price.text.strip().replace("\xa0", ' ') if start_price \
                                                                                                 is not None else None
    company_info_fz44[company]['purchase_link'] = link
    company_info_fz44[company]['document_link'] = get_document_fz44(link)
    company_info_fz44[company]['document_format'] = get_type_document_fz44(link)
    company_info_fz44[company]['documents'] = 1 if check_documents_fz44(link) else 0

    print(company_info_fz44)


def find_inn_fz44_link(link):
    req = requests.get(link, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    a_link = soup.find("span", class_='cardMainInfo__content').find_next().find_next().find_next().find_next()
    return a_link.get("href")


def find_inn_fz44(link):
    url = find_inn_fz44_link(link)
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")

    inn = soup.find("div", class_="registry-entry__body-value").find_next().find_next().find_next().find_next() \
        .find_next().find_next().find_next().find_next()
    if inn is None:
        return None
    else:
        return inn.text.strip()


def document_link_fz44(url):
    link_id = re.findall(r'\d+', url)
    if '/ea20/' in url:
        return f'https://zakupki.gov.ru/epz/order/notice/ea20/view/documents.html?regNumber={link_id[-1]}'
    elif '/zk20/' in url:
        return f'https://zakupki.gov.ru/epz/order/notice/zk20/view/documents.html?regNumber={link_id[-1]}'
    elif '/ea44/' in url:
        return f'https://zakupki.gov.ru/epz/order/notice/ea44/view/documents.html?regNumber={link_id[-1]}'
    elif '/ok20/' in url:
        return f'https://zakupki.gov.ru/epz/order/notice/ok20/view/documents.html?regNumber={link_id[-1]}'
    elif '/inm111/' in url:
        return f'https://zakupki.gov.ru/epz/order/notice/inm111/view/documents.html?regNumber={link_id[-1]}'
    elif '/ep44/' in url:
        return f'https://zakupki.gov.ru/epz/order/notice/ep44/view/documents.html?regNumber={link_id[-1]}'
    elif '/ok504' in url:
        return f'https://zakupki.gov.ru/epz/order/notice/ok504/view/documents.html?regNumber={link_id[-1]}'
    elif '/zk44/' in url:
        return f'https://zakupki.gov.ru/epz/order/notice/zk44/view/documents.html?regNumber={link_id[-1]}'
    elif '/ok44/' in url:
        return f'https://zakupki.gov.ru/epz/order/notice/ok44/view/documents.html?regNumber={link_id[-1]}'
    elif '/oku44/' in url:
        return f'https://zakupki.gov.ru/epz/order/notice/oku44/view/documents.html?regNumber={link_id[-1]}'
    elif '/za20/' in url:
        return f'https://zakupki.gov.ru/epz/order/notice/za20/view/documents.html?regNumber={link_id[-1]}'




def check_documents_fz44(url):
    documents_page = document_link_fz44(url)
    req = requests.get(documents_page, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    check = soup.find_all("span", class_="section__value")
    return check


def get_document_fz44(url):
    link = document_link_fz44(url)
    req = requests.get(link, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    document_dict = {}
    count = 1
    docs_list = soup.find_all("span", class_="section__value")
    for i in docs_list:
        document_dict[count] = i.find_next().get("href")
        count += 1
    return document_dict


def get_type_document_fz44(url):
    link = document_link_fz44(url)
    req = requests.get(link, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    type_dict = {}
    count = 1
    docs_list = soup.find_all("span", class_="section__value")
    for i in docs_list:
        temp = i.find_next().get("title")
        if '.docx' in temp or '.doc' in temp:
            type_dict[count] = "docx"
            count += 1
        elif '.rtf' in temp:
            type_dict[count] = "rtf"
            count += 1
        elif '.pdf' in temp:
            type_dict[count] = "pdf"
            count += 1
        elif '.zip' in temp:
            type_dict[count] = "zip"
            count += 1
        elif '.rar' in temp:
            type_dict[count] = "rar"
            count += 1
        elif '.7z' in temp:
            type_dict[count] = "7z"
            count += 1
        elif '.html' in temp:
            type_dict[count] = "html"
            count += 1
        elif '.excel' in temp:
            type_dict[count] = "excel"
            count += 1
        elif '.csv' in temp:
            type_dict[count] = "csv"
            count += 1
        elif '.xls' in temp:
            type_dict[count] = "xls"
            count += 1
        elif '.xlsx' in temp:
            type_dict[count] = "xlsx"
            count += 1
    return type_dict


def get_document_fz223(url):
    link = check_documents_fz223_link(url)
    req = requests.get(link, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    document_dict = {}
    count = 1
    docs_list = soup.find_all("span", class_="count")
    for i in docs_list:
        document_dict[count] = "https://zakupki.gov.ru" + i.find_next().find_next().find_next().find_next().get("href")
        count += 1
    return document_dict


def get_type_document_fz223(url):
    link = check_documents_fz223_link(url)
    req = requests.get(link, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    type_dict = {}

    count = 1
    docs_list = soup.find_all("img", class_="vAlignMiddle margRight5")
    for i in docs_list:
        temp = i.find_next().text.strip()
        if '.docx' in temp:
            type_dict[count] = "docx"
            count += 1
        elif '.rtf' in temp:
            type_dict[count] = "rtf"
            count += 1
        elif '.pdf' in temp:
            type_dict[count] = "pdf"
            count += 1
        elif '.zip' in temp:
            type_dict[count] = "zip"
            count += 1
        elif '.rar' in temp:
            type_dict[count] = "rar"
            count += 1
        elif '.7z' in temp:
            type_dict[count] = "7z"
            count += 1
        elif '.html' in temp:
            type_dict[count] = "html"
            count += 1
        elif '.excel' in temp:
            type_dict[count] = "excel"
            count += 1
        elif '.csv' in temp:
            type_dict[count] = "csv"
            count += 1
        elif '.xls' in temp:
            type_dict[count] = "xls"
            count += 1
        elif '.xlsx' in temp:
            type_dict[count] = "xlsx"
            count += 1
    return type_dict


