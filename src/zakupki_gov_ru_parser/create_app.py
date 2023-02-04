from src.zakupki_gov_ru_parser.parser import parse_resource
from zakupki_gov_ru_parser.external.minio.minio_utils import connect_to_minio


async def create_app():
    connect_to_minio()
    await parse_resource()
