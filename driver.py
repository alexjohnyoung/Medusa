from selenium.webdriver.common.by import By
import util 
import undetected_chromedriver as uc 


def medusa_goto(driver, url, headers=False, scroll=False):
    """
    Navigate the driver to a given URL.

    Args:
    - driver (WebDriver): The web driver object.
    - url (str): The URL to navigate to.
    - headers (bool/dict, optional): Headers to use while navigating. Defaults to False.
    - scroll (bool, optional): Whether to auto-scroll down on the page. Defaults to False.
    """

    if headers:
        driver.get(url, headers=headers)

    if scroll:
        for _ in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def medusa_get_random_proxy():
    """
    Get a random proxy from the list of proxies.

    Returns:
    - str: Randomly selected proxy.
    """

    proxies = util.medusa_get_setting("proxies")
    return proxies[util.randint(0, len(proxies)-1)]


def medusa_get_driver(profile=False, profile_str="", proxy=None, headless=False, strategy="normal", images=True):
    """
    Initialize and return a Chrome driver with given options.

    Args:
    - profile (bool, optional): Whether to use a profile. Defaults to False.
    - profile_str (str, optional): Path to the profile. Defaults to "".
    - proxy (str, optional): Proxy to use. Defaults to None.
    - headless (bool, optional): Whether to run browser in headless mode. Defaults to False.
    - strategy (str, optional): Page load strategy. Defaults to "normal".
    - images (bool, optional): Whether to load images. Defaults to True.

    Returns:
    - WebDriver: Configured Chrome driver.
    """

    driver = None

    options = uc.ChromeOptions()

    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--allow-profiles-outside-user-dir')
    options.add_argument('--enable-profile-shortcut-manager')
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    options.add_argument("--auto-open-devtools-for-tabs")

    options.page_load_strategy = strategy

    proxy_options = {}

    if proxy is not None:

        proxy_options = {
            'proxy': {
                'http': proxy,
                'https': proxy,
                'no_proxy': 'localhost,127.0.0.1'  # excludes
            }
        }

        if proxy != "any" and proxy != "null":
            options.add_argument(f'--proxy-server={proxy}')
        else:

            if util.medusa_has_setting("proxies_enabled"):

                options.add_argument(f'--proxy-server={medusa_get_random_proxy()}')

    if headless:
        options.add_argument("--headless")

    if not images:
        options.add_argument('--blink-settings=imagesEnabled=false')

    write_path = ""

    if profile_str != "":
        write_path = profile_str
        options.user_data_dir = write_path

    else:
        if profile is not False:
            write_path = f"C:/temp/"
            options.user_data_dir = write_path

    if proxy is not None:
        if profile_str != "":
            driver = uc.Chrome(options=options, seleniumwire_options=proxy_options)
        else:
            driver = uc.Chrome(options=options, seleniumwire_options=proxy_options)
    else:

        if profile_str != "":
            driver = uc.Chrome(user_data_dir=write_path, options=options)
        else:
            driver = uc.Chrome(options=options)

    print(f"Using {profile_str}")
    return driver


def medusa_download_find_url(bs):
    """
    Extract URL from a given string.

    Args:
    - bs (str): Input string to search for the URL.

    Returns:
    - tuple: Extracted URL and remainder string, or (False, 0) if not found.
    """

    _str = "v16-webapp.tiktok.com"

    find = bs.find(_str)
    bs = bs[find + 20:]

    if _str in bs:
        find = bs.find(_str)

        temp = bs[find:]

        bs = "https://" + bs[find - 5:] + '/'

        find = bs.find('"')

        temp = temp[find:]

        return bs[:find].replace("u002F", "").replace("\\", "/"), temp
    else:
        return False, 0


def medusa_scroll_window(driver, times):
    for _ in range(times):
        driver.execute_script("window.scrollTo(0, 300)")

def medusa_find_element_by_xpath(driver, elem, xpath):
    """
    Find an element on the page using its tag name and class.

    Args:
    - driver (WebDriver): The web driver object.
    - elem (str): The tag name of the element.
    - xpath (str): The class of the element.

    Returns:
    - WebElement/bool: Found element or False if not found.
    """

    element = driver.find_element(by=By.XPATH, value=f"//{elem}[@class='{xpath}']")

    if element:
        return element
    else:
        return False


def medusa_find_element_by_xpath_button(driver, xpath):
    """
    Find a button element on the page using its class.

    Args:
    - driver (WebDriver): The web driver object.
    - xpath (str): The class of the button element.

    Returns:
    - WebElement/bool: Found button element or False if not found.
    """

    element = driver.find_element(by=By.XPATH, value=f"//button[@class='{xpath}']")

    if element:
        return element
    else:
        return False


def medusa_find_element_by_xpath_span(driver, xpath):
    """
    Find a span element on the page using its class.

    Args:
    - driver (WebDriver): The web driver object.
    - xpath (str): The class of the span element.

    Returns:
    - WebElement/bool: Found span element or False if not found.
    """

    element = driver.find_element(by=By.XPATH, value=f"//span[@class='{xpath}']")

    if element:
        return element
    else:
        return False


def medusa_find_element_by_xpath_value(driver, elem, value):
    """
    Find an element on the page using its tag name and an attribute value.

    Args:
    - driver (WebDriver): The web driver object.
    - elem (str): The tag name of the element.
    - value (str): The attribute value for the element.

    Returns:
    - WebElement/bool: Found element or False if not found.
    """

    element = driver.find_element(by=By.XPATH, value=f"//{elem}{value}")

    if element:
        return element
    else:
        return False