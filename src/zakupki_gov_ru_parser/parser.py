import asyncio
import json
import re
import shelve
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
        await get_company_links(dict_links)
        dict_links = {}

        # #fz44
        # temp = await purchases_fz44_parser(target_company)
        # dict_links[target_company] = temp
        # print(dict_links)
        # await get_company_links(dict_links)
        # dict_links = {}


async def get_company_links(dict_company):
    for key, value in dict_company.items():
        for item in value:
            if not item:
                continue
            else:
                for i in item:
                    if not i:
                        continue
                    else:
                        get_company_info(i, key)


def get_company_info(link, company):
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
    documents = 0 if check_documents(link) is False else 1

    company_info_fz223[company]['number'] = number.text.strip()
    company_info_fz223[company]['status'] = status.text.strip() if status is not None else None
    company_info_fz223[company]['purchase_method'] = purchase.text.strip()
    company_info_fz223[company]['customer_inn'] = inn.text.strip()
    company_info_fz223[company]['start_price'] = start_price.text.strip().replace("\xa0", ' ') if start_price is not \
                                                                                                  None else None

    company_info_fz223[company]['documents'] = documents
    company_info_fz223[company]['purchase_link'] = link
    company_info_fz223[company]['document_link'] = check_documents_link(link)

    print(company_info_fz223)


def check_documents_link(url):
    link_id = re.findall(r'\d+', url)
    return f"https://zakupki.gov.ru/epz/order/notice/notice223/documents.html?noticeInfoId={link_id[-1]}"


def check_documents(url):
    temp_link = check_documents_link(url)
    req = requests.get(temp_link, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    title = soup.find("div", class_="attachment__value")
    if title:
        return True
    else:
        return False

