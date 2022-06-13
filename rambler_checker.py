# -*- coding: utf8 -*-
import os
import imaplib
import email
import json
import time
from urllib3 import disable_warnings
from loguru import logger
from sys import stderr
from os import system

disable_warnings()


def clear(): return system('cls')


logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white>"
                          " | <green>{level: <8}</green>"
                          " | <cyan>{line}</cyan>"
                          " - <white>{message}</white>")

print('Rambler Checker | by cringecode')


def get_username():
    with open("ramblers.txt", "r") as file:
        username = [row.strip().split(":")[0] for row in file]
        return username


def get_pswd():
    with open("ramblers.txt", "r") as file:
        password = [row.strip().split(":")[1] for row in file]
        return password


def main():
    count = 0
    time_string = time.strftime("%m.%d.%Y")
    if os.path.exists("check.json"):
        os.remove("check.json")
    try:
        while count != len(get_username()):
            mail = imaplib.IMAP4_SSL("imap.rambler.ru", port=993)
            mail.login(get_username()[count], get_pswd()[count])
            mail.select("Inbox")
            _, msgnums = mail.search(None, "ALL")

            json_data = {
                get_username()[count]: []
            }
            for msgnum in msgnums[0].split():
                _, data = mail.fetch(msgnum, "(RFC822)")
                message = email.message_from_bytes(data[0][1])

                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        content_message = part.as_string()
                        content_message = content_message.split("UTF-8")[1].replace("\n", "").replace('"', "")
                        from_email = message.get('From').split("<")[1].split(">")[0]
                        bcc_email = message.get('BCC')
                        date_email = message.get('Date')
                        subject_email = message.get("Subject")
                        email_content = content_message

                if email_content not in json_data[get_username()[count]]:
                    json_data[get_username()[count]].append({"Email": from_email,
                                                             "Subject": subject_email,
                                                             "Date": date_email,
                                                             "Content": email_content})

            with open(f"check.json", "a", encoding="utf-8") as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)

            logger.info(f"{get_username()[count]} успешно обработана!")

            count += 1
            mail.logout()

    except Exception:
        with open(f"Logs\{time_string}.txt", "a", encoding="utf-8") as file:
            file.write(f"{get_username()[count]} не был обработана!")
    finally:
        print("Работа успешно выполнена!")


if __name__ == "__main__":
    main()
