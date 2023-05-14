from colorama import Fore
from enum import Enum
import datetime
import telebot
import logging

logging.basicConfig(level=logging.DEBUG, filename="logs.log", filemode="w",
                    format='[%(asctime)s] %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
users = []


class Loglevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


def send(message: telebot.types.Message, level: Loglevel, log_mes: str, error: Exception = None):
    """
    This function sends to the console and saves to a log file.

    :param message: telebot.types.Message
    :param level: Loglevel
    :param log_mes: message log
    :param error: error message

    :return: None
    """
    global users
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if not message.chat.id in users:
        users.append(message.chat.id)
        logging.info(f"New user {message.chat.id}")
        print(Fore.GREEN + f"[{time}] INFO New user {message.chat.id}")

    if level == Loglevel.DEBUG:
        logging.debug(log_mes)
        print(Fore.BLUE + f"[{time}] DEBUG {log_mes}", error)
    elif level == Loglevel.INFO:
        logging.info(log_mes)
        print(Fore.GREEN + f"[{time}] INFO {log_mes}", error)
    elif level == Loglevel.WARNING:
        logging.debug(log_mes)
        print(Fore.YELLOW + f"[{time}] WARNING {log_mes}", error)
    elif level == Loglevel.ERROR:
        logging.error(log_mes, exc_info=error)
        print(Fore.RED + f"[{time}] ERROR {log_mes}", error)
    elif level == Loglevel.CRITICAL:
        logging.critical(log_mes)
        print(Fore.RED + f"[{time}] CRITICAL {log_mes}", error)
