import aiohttp
from bs4 import BeautifulSoup as Bs

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor


token_api = "5366991699:AAHEdByWeyS5ttagGpZhZ9EIXhPJfv65Ab0"
bot = Bot(token=token_api, parse_mode=types.ParseMode.HTML)
dispatcher = Dispatcher(bot)


async def get_ex_rate():
    currency = {}
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.188 Safari/537.36 CrKey/1.54.250320",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get("http://www.cbr.ru/scripts/XML_daily.asp", headers=header) as response:
            status_response = response.status
            if status_response == 200:
                soup = Bs(str(await response.text()).encode('cp1251'), "xml", exclude_encodings="utf-8")
                char_codes = (i.get_text() for i in soup.find_all("CharCode"))
                nominals = (i.get_text() for i in soup.find_all("Nominal"))
                names = (i.get_text() for i in soup.find_all("Name"))
                values = (i.get_text() for i in soup.find_all("Value"))
                information = zip(names, char_codes, nominals, values)
                for name, char_code, nominal, value in information:
                    currency[str(char_code)] = {
                        "name": str(name),
                        "nominal": float(nominal.replace(",", ".")),
                        "value": float(value.replace(",", "."))
                    }
                return currency
            else:
                return "(Error) Сервер не смог получить данные, попробуйте чуть позже"


@dispatcher.message_handler(commands=["start", "help"])
async def function_with_starting_commands(message: types.Message):
    message_lower = message.text.lower()
    if message_lower == "/help":
        message_for_user = """
Команды бота:
1) /GetExchangeRates - получить курс валют
2) Для получения курса определённой валюты, отправьте код валюты боту ("USD", "DKK")
"""
        await message.answer(message_for_user)
    else:
        await message.answer("Привет, пользователь!\nБот поможет узнать курсы валют 💰\n\nПомощь: /help")


@dispatcher.message_handler(commands=["GetExchangeRates"])
async def get_exchange_rate(message: types.Message):
    currency = await get_ex_rate()
    if "(Error)" in currency:
        await message.answer(currency)
    else:
        message_for_user = "Курсы валют (за 1 ед.):"
        for char_code in currency:
            block_i = currency[char_code]
            message_for_user += f'\n\n{char_code} - {block_i["name"]}\n-> Value: {round(block_i["value"] / block_i["nominal"], 3)}'
        await message.answer(message_for_user)


@dispatcher.message_handler(content_types=['text'])
async def get_value_for_char_code(message: types.Message):
    currency = await get_ex_rate()
    char_code = message.text.upper()
    if "(Error)" in currency:
        await message.answer(currency)
    else:
        if char_code in currency:
            message_for_user = "Курсы валют (за 1 ед.):"
            block_i = currency[char_code]
            message_for_user += f'\n\n{char_code} - {block_i["name"]}\n-> Value: {round(block_i["value"] / block_i["nominal"], 3)}'
        else:
            message_for_user = "Мы не следим за этой валютой"
        await message.answer(message_for_user)


if __name__ == '__main__':
    executor.start_polling(dispatcher)

# End Page
