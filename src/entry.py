from os import stat
import telegram
import subprocess
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
import json
import logging
from expiringdict import ExpiringDict

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

questions = [
    {'Q': "Are you concerned that you or your patient could have mucormycosis? Does your patient currently have covid or did they recover from covid in the last 30 days?",
     'A': [
         ("Yes", 1),
         ("No", 0)]},
    {'Q': """Does the patient have any of the following conditions?
Type 2 diabetes mellitus
History of organ transplant
History of cancer (malignancy) or burns
Malnutrition """,
     'A': [("Yes", 1),
           ("No", 0)]},
    {'Q': """Have they taken oral or injectable corticosteroids like methylprednisolone or dexamethasone? """,
     'A': [("Yes", 1),
           ("No", 0)]},
    {'Q': """Did they have a prolonged ICU stay (more than 4-5 days) for covid treatment? """,
     'A': [("Yes", 1),
           ("No", 0)]},
    {'Q': "Do they have nasal discharge? ",
     'A': [("Yes", 1),
           ("Yes, bloody red or blackish colored", 2),
           ("No", 0)]},
    {'Q': """Do they have facial swelling numbness or pain?
Do they have pain over the cheek bones? """,
     'A': [("Yes", 1),
           ("No", 0)]},
    {'Q': "Do they have abnormal blackish discoloration over the eyes, in the skin over the nose or in the mouth? ",
     'A': [("Yes", 1),
           ("No", 0)]},
    {'Q': "Do they have toothaches, feel a loosening of one of their teeth, or feel pain or swelling in the jaw? ",
     'A': [("Yes", 1),
           ("No", 0)]},
    {'Q': "Do they have blurred vision or double vision associated with eye pain? (new onset and not related to spectacles) ",
     'A': [("Yes", 1),
           ("No", 0)]},
    {'Q': "Have they recently recovered from covid and are having chest pain, fever, blood stained cough or breathing difficulties? ",
     'A': [("Yes", 1),
           ("No", 0)]},
]

user_status = {}

initial_data = {'stage': 0, 'score': 0}

def getRiskLevel(score):
    if score< 3:
        return "This patient is at minimal risk, and there is no need to worry unless they get more symptoms."
    elif score <5:
        return "This patient is at low risk for mucormycosis, and should get checked by a doctor if they have any symptoms."
    elif score < 8:
        return "This patient is at moderate risk and should consult an ent specialist to rule out mucormycosis."
    else:
        return "This patient is at high risk for mucormycosis as per your responses, and should consult an ent specialist, dental surgeon or ophthalmologist depending on their symptoms."

def entry(bot, update):
    print(user_status)
    print(initial_data)
    try:
        # res = bot.send_message(chat_id="-1001164870268", text=json.dumps(update.to_dict(), indent=2))
        # print(json.dumps(update.to_dict(), indent=2))
        logging.info(update)
        pass
    except Exception as e:
        logging.error(e)
        # bot.send_message(chat_id="-1001164870268", text=str(e))
    if update.message and update.message.text:
        chat_id = update.message.chat_id
        if chat_id not in user_status:
            user_status[chat_id] = initial_data.copy()
        if update.message.text == "/start":
            user_status[chat_id] = initial_data.copy()
        if update.message.text == "/cancel":
            del user_status[chat_id]
            bot.sendMessage(chat_id=update.message.chat_id,
                            text="Operation cancelled. Send /start to continue", reply_markup=ReplyKeyboardRemove())
            return
        if user_status[chat_id]['stage'] > 0:
            answers = questions[(user_status[chat_id]['stage'])-1]['A']
            for a in answers:
                if update.message.text in a:
                    user_status[chat_id]['score'] = user_status[chat_id]['score'] + a[1]
                    break
        if user_status[chat_id]['stage'] < len(questions):
            answers = questions[(user_status[chat_id]['stage'])]['A']
            ans_list = [[i[0]] for i in answers]
            bot.sendMessage(chat_id=update.message.chat_id,
                            text=questions[user_status[chat_id]['stage']]['Q'],
                            reply_markup=ReplyKeyboardMarkup(ans_list))
            user_status[chat_id]['stage'] = user_status[chat_id]['stage']+1
        else:
            bot.sendMessage(chat_id=update.message.chat_id,
                            text=getRiskLevel(user_status[chat_id]['score'])+
                            "\n\nSend /start to start over", reply_markup=ReplyKeyboardRemove())
            bot.sendDocument(chat_id=update.message.chat_id, document="BQACAgUAAxkDAAIB1WCtuxPgY7iBLYCta-xejxxSHxjdAAI7AgACxP5gVfL8CC0pN1ErHwQ")
