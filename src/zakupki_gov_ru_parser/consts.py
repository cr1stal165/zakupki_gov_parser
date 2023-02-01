USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3",
)

ACCEPT = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
TIMEOUT = 10.0

BASE_LINK = "https://zakupki.gov.ru"
RECORDS_PER_PAGE = 50


BASE_QUERY_PARAMS = {
    "morphology": "on",
    "search-filter": "Дате+размещения",
    "pageNumber": 1,
    "sortDirection": False,
    "recordsPerPage": RECORDS_PER_PAGE,
    "showLotsInfoHidden": False,
    "sortBy": "UPDATE_DATE",
    "pc": "on",
    "currencyIdGeneral": -1,
}
