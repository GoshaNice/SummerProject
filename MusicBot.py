from bs4 import BeautifulSoup
import requests
import telebot
from telebot import types
from gtts import gTTS


class MusicFinder:
    def __init__(self,
                 song_name: str): #функция раскрывает сообщение пользователя и вытаскивает имя исполнителя и название песни
        singer, song = song_name.split("/")
        singer = singer.lower()
        singer = singer.replace(" ", "_")
        song = song.lower()
        song = song.replace(" ", "_")
        self._song_name = song_name
        self._singer = singer
        self._song = song
        self._url = self._singer[0] + "/" + self._singer + "/" + self._song

    def find_original_text(self) -> str: #функция парсит сайт и находит оригинальный текст песни на английском языке
        url = f'https://en.lyrsense.com/{self._singer}/{self._song}'
        response = requests.get(url)

        if response.status_code != 200:
            return "Приношу свои извинения, я не смог найти данную песню"

        soup = BeautifulSoup(response.text, 'lxml')
        types_1 = soup.find_all("span", "puzEng")
        final_answer = ""
        for i in types_1:
            final_answer += i.text
            final_answer += "\n"
        return final_answer

    def find_translation(self) -> str: #функция парсит сайт и находит перевод текста песни на русский язык
        url = f'https://en.lyrsense.com/{self._singer}/{self._song}'
        response = requests.get(url)

        if response.status_code != 200:
            return "Приношу свои извинения, я не смог найти данную песню"

        soup = BeautifulSoup(response.text, 'lxml')
        types_1 = soup.find_all("p", id == "ru_text")[1]
        final_answer = ""
        for i in types_1:
            final_answer += i.text
            final_answer += "\n"
        return final_answer

    def dub_song(self): #функция берет английский текст песни и озвучивает его
        txt = self.find_original_text()
        myobj = gTTS(text=txt, lang="en", slow=False)
        myobj.save('bad_words_in_strange_order.mp3')


bot = telebot.TeleBot("1824128367:AAEThtMft1hFinf7j74GqiSgRhERwP142ZY") #можете забирать, мне не жалко


@bot.message_handler(commands=['start', 'help']) 
def send_keyboard(message, text="Привет, я музбот! Я умею находить слова английских песен и их переводы! "
                                "Давай Начнем?"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2) 
    itembtn1 = types.KeyboardButton('Найти текст песни')
    itembtn2 = types.KeyboardButton('Найти перевод песни')
    itembtn3 = types.KeyboardButton('Озвучь песню')
    itembtn4 = types.KeyboardButton('Заканчиваем')
    keyboard.add(itembtn1, itembtn2)
    keyboard.add(itembtn3, itembtn4)
    msg = bot.send_message(message.from_user.id,
                           text=text, reply_markup=keyboard)
    bot.register_next_step_handler(msg, callback_worker)


def search_song(msg): #функция, которая ищет английский текст песни
    bot.send_message(msg.chat.id, f'Операция выполняется, пытаюсь найти текст для : {msg.text}')
    song_name = msg.text
    music_bot = MusicFinder(song_name)
    txt = music_bot.find_original_text()
    bot.send_message(msg.chat.id, txt)
    send_keyboard(msg, "Чем еще могу помочь?")


def search_translation(msg): #функция, которая ищет перевод на русский
    bot.send_message(msg.chat.id, f'Операция выполняется, пытаюсь найти перевод для : {msg.text}')
    song_name = msg.text
    music_bot = MusicFinder(song_name)
    txt = music_bot.find_translation()
    bot.send_message(msg.chat.id, txt)
    send_keyboard(msg, "Чем еще могу помочь?")


def dub_song(msg): #функция, которая отсылает озвученный английский текст
    bot.send_message(msg.chat.id, f'Операция выполняется, пытаюсь найти исполнение для, '
                                  f'операция может занять некоторое время : {msg.text}')
    song_name = msg.text
    music_bot = MusicFinder(song_name)
    music_bot.dub_song()
    bot.send_audio(msg.chat.id, audio=open("bad_words_in_strange_order.mp3", 'rb'))
    send_keyboard(msg, "Чем еще могу помочь?")


def callback_worker(call): #центр управления
    if call.text == "Найти текст песни":
        msg = bot.send_message(call.chat.id,
                               'Давайте найдем текст песни! Напишите имя исполнителя и название песни через /. '
                               'Например: Sia/Chandelier')
        bot.register_next_step_handler(msg, search_song)
    elif call.text == "Найти перевод песни":
        msg = bot.send_message(call.chat.id,
                               'Давайте найдем перевод песни! Напишите имя исполнителя и название песни через /. '
                               'Например: Sia/Chandelier')
        bot.register_next_step_handler(msg, search_translation)
    elif call.text == "Озвучь песню":
        msg = bot.send_message(call.chat.id,
                               'Давайте сделаем озвучку песни! Напишите имя исполнителя и название песни через /. '
                               'Например: Sia/Chandelier')
        bot.register_next_step_handler(msg, dub_song)

    elif call.text == "Заканчиваем":
        bot.send_message(call.chat.id, 'Хорошего дня! Когда захотите продолжнить нажмите на команду /start')


@bot.message_handler(content_types=['text'])
def handle_docs_audio(message):
    send_keyboard(message, text="Я не понимаю, выберите один из пунктов: ")


bot.polling(none_stop=True)
