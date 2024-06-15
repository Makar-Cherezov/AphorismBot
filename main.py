#!/usr/bin/python3.4

import telebot
import requests
from bs4 import BeautifulSoup


token = "5586927712:AAFhmpOYByhi18KrcVCwnywkvg0zMHiJX_A"
bot = telebot.TeleBot(token)
welcome_text = "Приветствую! Этот бот поможет пополнить багаж афоризмов и притч. Что он умеет?\n" \
               "Бот поддерживает следующие команды:\n" \
               "/getquote - прочитайте одну из избранных цитат прямо в телеграм-канале!\n" \
               "/getstory -  введите эту команду, и в ответ получите одну из множества мудрых притч!\n" \
               "Также бот поддерживает inline-запросы! Наберите имя бота @AphorBot и слово/словосочетание для поиска по сайту!\n\n" \
               "Афоризмы и притчи взяты с сайта aphoristic-world.ru. Проект разработан @styrtet_keiser."
links = []

def parse_quote():
    response = requests.get(url='http://aphoristic-world.ru/')
    soup = BeautifulSoup(response.text, 'lxml')
    return soup.find('div', class_='sprocket-mosaic-text').text.strip()


def parse_parable():
    response = requests.get(url='http://aphoristic-world.ru/')
    soup = BeautifulSoup(response.text, 'lxml')
    header = soup.find('a', class_='uk-link-reset').text.strip()
    text = soup.find('div', class_='uk-margin').text.strip()
    return header, text


def create_search_url(qrtext='text'):
    words = qrtext.strip().split()
    search_request = '%20'.join(words)

    search_url = "http://aphoristic-world.ru/search.html?searchword="+search_request+"&ordering=alpha&searchphrase=any&limit=50"
    return search_url


def parse_results(search_request='сила'):
    response = requests.get(url=create_search_url(search_request))
    soup = BeautifulSoup(response.text, 'lxml')
    global links
    links = soup.select('dl a')
    results = soup.find_all('dd', class_='result-text')
    quotes = []
    for quote in results:
        quotes.append(quote.text.strip())
    if "По алфавиту" in quotes[0]:
        quotes = quotes[1:]
    return quotes


@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    bot.send_message(message.chat.id, welcome_text)


@bot.message_handler(commands=['getquote'])
def send_quote(message):
    bot.send_message(message.chat.id, parse_quote())


@bot.message_handler(commands=['getstory'])
def send_parable(message):
    parable_title, parable_text = parse_parable()
    parable = parable_title + '\n' + parable_text
    bot.send_message(message.chat.id, parable)

@bot.inline_handler(lambda query: type(query.query) == str)
def inline_handler(inline_query='пример'):
    results_text = parse_results(inline_query.query.strip())
    results = []
    try:
        for i in range(len(results_text)):
            try:
                url = "http://aphoristic-world.ru" + links[i]["href"]
            except Exception:
                url = "http://aphoristic-world.ru"
            results.append(telebot.types.InlineQueryResultArticle(i, results_text[i], telebot.types.InputTextMessageContent(results_text[i])))
        bot.answer_inline_query(inline_query.id, results)
    except Exception:
        bot.send_message(inline_query.from_user.id, "Упс, что-то пошло не так с этим запросом. Попробуйте другой.")

bot.infinity_polling()
