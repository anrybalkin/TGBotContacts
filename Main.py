# coding: utf8
from array import ArrayType
from asyncio.windows_events import NULL
from random import random
from telethon.sync import TelegramClient
from telethon import TelegramClient, client
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.types import InputPhoneContact
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon import functions, types
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os.path
import json
import sys

# Remember to use your own values from my.telegram.org!
api_id = "id"
api_hash = "hash"
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = ''
SAMPLE_RANGE_NAME = ''
SAMPLE_RANGE_NUMBER = ''
phone = ""
# data


def main(phone=""):
    if phone == "":
        print("Введите номер на который нужно импортровать контакты")
        phone = str(input())
    # Login
    client = TelegramClient(phone, api_id, api_hash)
    client.connect()

    if not client.is_user_authorized():
        client.send_code_request(phone)
        client.sign_in(phone, input('Enter the code: '))
    ContactsValues = GetContacts()
    Result = list()
    for contact in range(len(ContactsValues)):
        # add user to array+380xxxxxxxxx
        print(str(ContactsValues[contact][0]).replace(
            "['", "").replace("']", ""))
        phoneNum = str(ContactsValues[contact][0]).replace(
            "['", "").replace("']", "")
        print(str(ContactsValues[contact][1]).replace(
            "['", "").replace("']", ""))
        fullname = str(ContactsValues[contact][1]).replace(
            "['", "").replace("']", "")
        nameF = fullname.split(" ")[0]
        print(nameF)
        nameL = ""
        if len(fullname.split(" ")) > 1:
            nameL = fullname.split(" ")[1]
        contactCel = InputPhoneContact(
            client_id=0, phone=phoneNum, first_name=nameF, last_name=nameL)
        Result.append(contactCel)
    result = client(ImportContactsRequest(Result))


def GetContacts():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    resultNames = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                     range=SAMPLE_RANGE_NAME).execute()
    resultNumbers = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                       range=SAMPLE_RANGE_NUMBER).execute()
    valueName = resultNames.get('values', [])
    valueNumbers = resultNumbers.get('values', [])

    if not valueName and not valueNumbers:
        print('No data found.')
    else:
        print('Name, Major:')
        d1 = []
        for i in range(len(valueNumbers)):
            d1.append([valueNumbers[i], valueName[i]])
        return d1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        phone = format(sys.argv[1])
    if os.path.exists("settings.json"):
        # Opening JSON file
        f = open('settings.json',)
        # returns JSON object as
        # a array settings
        data = json.load(f)
        # save parametrs from file
        SAMPLE_SPREADSHEET_ID = data["SHEET_ID"]
        SAMPLE_RANGE_NAME = data["SHEET_COLUMN_NAME"]
        SAMPLE_RANGE_NUMBER = data["SHEET_COLUMN_PHONE"]
        # Closing file
        f.close()
        main(phone)
    else:
        print("Для работы приложения необходимо что бы ввели некоторые параметры или разместили конфигурационный рядом с программой и перезапустили программу")
        print("Введите ID гугл таблицы")
        SAMPLE_SPREADSHEET_ID = str(input())
        print("Введите имя листа с которого будет считиватся данные")
        listN = str(input())
        print("Введите диапазон ячеек латиницей с которых будет считыватся имена")
        SAMPLE_RANGE_NAME = listN + "!"+str(input())
        print("Введите диапазон ячеек латиницей с которых будет считыватся номера")
        SAMPLE_RANGE_NUMBER = listN+"!" + str(input())
        settings = {
            "SHEET_ID": SAMPLE_SPREADSHEET_ID,
            "SHEET_COLUMN_NAME": SAMPLE_RANGE_NAME,
            "SHEET_COLUMN_PHONE": SAMPLE_RANGE_NUMBER
        }
        with open("settings.json", "w", encoding='utf-8') as outfile:
            json.dump(settings, outfile)
        main(phone)
