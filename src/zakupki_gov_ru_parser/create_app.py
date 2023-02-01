from src.zakupki_gov_ru_parser.parser import parse_resource


async def create_app():
    await parse_resource()
