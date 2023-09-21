from os.path import exists, dirname, abspath, getsize
from os import mkdir, system, listdir, rmdir, remove
from sys import argv
from time import sleep
from shutil import rmtree
from random import randint, choice
from colorama import Fore, Style
import threading
import json

LOGO = f'''
███╗   ███╗███████╗██████╗ ██╗   ██╗███████╗ █████╗ 
████╗ ████║██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗
██╔████╔██║█████╗  ██║  ██║██║   ██║███████╗███████║
██║╚██╔╝██║██╔══╝  ██║  ██║██║   ██║╚════██║██╔══██║
██║ ╚═╝ ██║███████╗██████╔╝╚██████╔╝███████║██║  ██║
╚═╝     ╚═╝╚══════╝╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝
'''
MEDUSA_PATH = ""
MEDUSA_EXE = ""
MEDUSA_CHUNK_SIZE = 2048
MEDUSA_VISITED_MENU = False
MEDUSA_PAGE = "main_menu"
MEDUSA_PROCEDURE = {}
MEDUSA_THREADS = []
MEDUSA_PROXIES = []
MEDUSA_TEMP = []
MEDUSA_LINKED_THREADS = {}
MEDUSA_JOBS_LISTENING = []
MEDUSA_JOB_VIEW = 0
MEDUSA_JOB_OVERVIEW = []
MEDUSA_MAX_JOBS = 5
MEDUSA_JOBS_QUEUE = []
MEDUSA_DATA_SAVES = {}
MEDUSA_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
]
MEDUSA_SETTINGS = {}

def medusa_get_data_save(name):
    """
    Retrieve data save cookies based on a provided name.

    Args:
        name (str): The name of the data save to fetch.

    Returns:
        tuple: A tuple containing an empty dictionary and the corresponding cookies.
              Returns an empty dictionary if the name is not found.
    """

    for entry in MEDUSA_DATA_SAVES:
        if MEDUSA_DATA_SAVES[entry]['name'] == name:
            return {}, MEDUSA_DATA_SAVES[entry]['cookies']

    return {}


def medusa_has_save_field(name):
    """
    Check the existence of a save field with a given name.

    Args:
        name (str): Name of the save field to check.

    Returns:
        bool: True if the save field exists, False otherwise.
    """
    return exists(MEDUSA_PATH + f"data/{name}.txt")


def medusa_save_data(name, headers, cookies):
    """
    Persist provided data (headers and cookies) under a specified name.

    Args:
        name (str): The name under which data should be saved.
        headers (dict): The headers to be saved.
        cookies (dict): The cookies to be saved.
    """

    write_tab = {
        'headers': {},
        'cookies': {}
    }

    for header in headers:
        if "user-agent" not in header.lower():
            write_tab['headers'][header] = headers[header]
        else:
            write_tab['headers']['user-agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"

    write_tab['cookies'] = cookies

    file_handle = open(MEDUSA_PATH + f"data/{name}.txt", "w")
    file_handle.write(json.dumps(write_tab))
    file_handle.close()


def medusa_load_data_saves():
    """
    Load and parse all data saves from the 'data' directory.

    Returns:
        int: The number of data saves loaded.
    """

    if not exists(MEDUSA_PATH + "data"):
        mkdir(MEDUSA_PATH + "data")
        return

    files = listdir("data/")

    num_entries = len(MEDUSA_DATA_SAVES)

    for file in files:

        if ".txt" not in file:
            continue

        file_handle = open(MEDUSA_PATH + f"data/{file}", "r")
        file_data = file_handle.read()
        file_handle.close()

        json_data = json.loads(file_data)

        file = file.replace(".txt", "")

        MEDUSA_DATA_SAVES[num_entries] = {"name": file, "headers": json_data["headers"], "cookies": json_data["cookies"]}
        num_entries += 1

    return num_entries


def medusa_add_setting(name, value):
    """
    Add a new setting or append a value to an existing setting.

    Args:
        name (str): Name of the setting.
        value (Any): Value to be added or appended to the setting.
    """

    num_settings = len(MEDUSA_SETTINGS)

    has_setting = -1

    for key, entry in enumerate(MEDUSA_SETTINGS):
        if MEDUSA_SETTINGS[entry]['name'] == name:
            has_setting = entry
            break

    if has_setting == -1:

        _highest = 0

        for key, val in enumerate(MEDUSA_SETTINGS):

            val = int(val)

            if val > _highest:
                _highest = val

        _highest = _highest + 1

        MEDUSA_SETTINGS[_highest] = {'name': name, 'value': [value]}

    else:
        MEDUSA_SETTINGS[has_setting]['value'].append(value)

    medusa_save_settings()


def medusa_set_setting(name, value):
    """
    Modify the value of a given setting.

    Args:
        name (str): Name of the setting to modify.
        value (Any): New value for the setting.
    """

    num_settings = len(MEDUSA_SETTINGS)

    has_setting = -1
    found = False

    if len(value) == 0:
        medusa_remove_setting(name)
        return

    for key, entry in enumerate(MEDUSA_SETTINGS):
        if MEDUSA_SETTINGS[entry]['name'] == name:
            has_setting = entry
            found = True
            break

    if found:
        MEDUSA_SETTINGS[has_setting] = {'name': name, 'value': value}

    medusa_save_settings()


def medusa_has_setting(name):
    """
    Check if a specific setting exists.

    Args:
        name (str): Name of the setting to check.

    Returns:
        bool: True if the setting exists, False otherwise.
    """

    if name == "download_by_caption":
        return True

    for key, entry in enumerate(MEDUSA_SETTINGS):
        if MEDUSA_SETTINGS[entry]['name'] == name:
            return True

    return False


def medusa_get_setting(name):
    """
    Retrieve the value of a specific setting.

    Args:
        name (str): Name of the setting to retrieve.

    Returns:
        Any: Value of the setting, or False if the setting is not found.
    """

    for key, entry in enumerate(MEDUSA_SETTINGS):
        if MEDUSA_SETTINGS[entry]['name'] == name:
            return MEDUSA_SETTINGS[entry]['value']

    return False


def medusa_remove_setting(name):
    """
    Remove a specified setting.

    Args:
        name (str): Name of the setting to remove.
    """

    for key, entry in enumerate(MEDUSA_SETTINGS):
        if MEDUSA_SETTINGS[entry]['name'] == name:
            del MEDUSA_SETTINGS[entry]
            break

    medusa_save_settings()


def medusa_save_settings():
    """
    Persist current settings to a file.
    """

    settings_handle = open(MEDUSA_PATH + "settings.txt", "w")

    _json = json.dumps(MEDUSA_SETTINGS)

    settings_handle.write(_json)

    settings_handle.close()


def medusa_load_settings():
    """
    Load settings from a file into the global MEDUSA_SETTINGS variable.
    """
    global MEDUSA_SETTINGS

    if not exists(MEDUSA_PATH + "settings.txt"):
        return

    settings_handle = open(MEDUSA_PATH + "settings.txt", "r")
    settings_data = settings_handle.read()
    settings_handle.close()

    settings_data = json.loads(settings_data)

    MEDUSA_SETTINGS = settings_data


def medusa_reset_page():
    """
    Reset the global page variable to 'main_menu'.
    """

    global MEDUSA_PAGE
    MEDUSA_PAGE = "main_menu"


def medusa_get_random_word(num_chars):
    """
    Generate a random string of uppercase letters.

    Args:
        num_chars (int): Length of the random string.

    Returns:
        str: Randomly generated string.
    """

    _str = ""

    for i in range(num_chars):
        _rand = randint(66, 88)
        _str += chr(_rand)

    return _str


def medusa_type_keys(element, _str):
    """
    Simulate typing keys into a given element with a delay.

    Args:
        element (Any): The target element to type into.
        _str (str): The string to be typed.
    """

    for ch in _str:
        element.send_keys(ch)
        sleep(0.3)


def medusa_input(txt):
    """
    Prompt the user for integer input with a specified message.

    Args:
        txt (str): Message to display to the user.

    Returns:
        int: User's input as an integer.
    """

    while True:
        try:
            _data = int(input("[" + Fore.RED + "Medusa" + Style.RESET_ALL + "]: " + txt))
            break
        except ValueError:
            pass

    return _data


def medusa_no_prompt_input():
    """
    Wait for the user to provide an integer input without any prompts.

    Returns:
        int: User's input as an integer.
    """

    while True:
        try:
            _data = int(input(""))
            break
        except ValueError:
            pass

    return _data


def medusa_str_input(txt):
    """
    Prompt the user for string input with a specified message.

    Args:
        txt (str): Message to display to the user.

    Returns:
        str: User's input as a string.
    """

    _data = input("[" + Fore.RED + "Medusa" + Style.RESET_ALL + "]: " + txt)

    return _data


def medusa_nprint(txt):
    """
    Print a message in a specified color.

    Args:
        txt (str): Message to print.
    """

    print(Fore.RED + txt)


def medusa_print(txt):
    """
    Print a message with a Medusa prefix in a specified color.

    Args:
        txt (str): Message to print.
    """

    print("[" + Fore.RED + "Medusa" + Style.RESET_ALL + "]: " + txt)


def medusa_sleep(time):
    """
    Pause the program for a specified amount of seconds and notify the user.

    Args:
        time (int): Number of seconds to pause.
    """

    medusa_print(f"Sleeping for {time}s..")
    sleep(time)


def medusa_logo():
    """
    Clear the console and print the Medusa logo in a specified color.
    """

    print("\033[H\033[J", end="")
    print(Fore.RED + LOGO + Style.RESET_ALL)


def medusa_get_random_useragent():
    """
    Retrieve a random user-agent from the global list.

    Returns:
        str: A random user-agent string.
    """
    global MEDUSA_USER_AGENTS

    index = randint(0, len(MEDUSA_USER_AGENTS)-1)
    return MEDUSA_USER_AGENTS[index]


def medusa_random_letters():
    """
    Generate a random string of 13 characters, ranging from uppercase A-Z to lowercase a-b.

    Returns:
        str: Randomly generated string.
    """

    txt = ""

    for i in range(13):
        txt += chr(randint(66, 98))

    return txt
