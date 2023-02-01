import asyncio

from src.zakupki_gov_ru_parser.create_app import create_app


async def main():
    await create_app()


if __name__ == "__main__":
    asyncio.run(main())
