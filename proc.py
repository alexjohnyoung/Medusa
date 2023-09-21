import util 
import driver as dr 
import jobs 

import threading
from requests import Session, get
from requests.exceptions import ConnectionError
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException, \
    UnexpectedAlertPresentException, ElementClickInterceptedException

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from bs4 import BeautifulSoup
import json


def medusa_proc_tiktok_download_by_name():
    """
    Prompt the user for a TikTok profile name and start a job to download
    all videos from the provided profile. If the input is 'n', the function
    returns without doing anything.
    """

    profile_name = util.medusa_str_input("Please enter profile name (or 'n' to cancel): ")

    if profile_name == 'n':
        return

    jobs.medusa_start_job(medusa_proc_tiktok_helper_download_all_videos, (profile_name,))


def medusa_proc_tiktok_download_by_keyword():
    """
    Prompt the user for a keyword. Using the entered keyword, start a job
    to find TikTok profiles associated with the keyword.
    """

    keyword = util.medusa_str_input("Please enter keyword: ")

    jobs.medusa_start_job(medusa_proc_tiktok_helper_find_profile, (keyword,))


def medusa_proc_tiktok_helper_find_profile(keyword):
    """
    Use the provided keyword to search for TikTok profiles.

    Parameters:
    - keyword (str): Keyword to search TikTok profiles.

    This function builds a search URL using the keyword, makes a web request,
    parses the response to extract TikTok profile links associated with the
    keyword, and starts new jobs to download videos from those profiles.
    """

    current_thread = threading.current_thread()

    util.sleep(0.5)

    if type(keyword) != "string":
        keyword = ''.join(keyword)

    url = f"https://www.tiktok.com/search/user?q={keyword}"

    #url = f"http://www.tiktok.com/api/search/user/full/?aid=1988&app_language=en&app_name=tiktok_web&battery_info=1&browser_language=en-US&browser_name=Mozilla&browser_online=true&browser_platform=Win32&browser_version=5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F107.0.0.0%20Safari%2F537.36&channel=tiktok_web&cookie_enabled=true&cursor=0&device_id=7443378182761118854&device_platform=web_pc&focus_state=true&from_page=search&history_len=6&is_fullscreen=false&is_page_visible=true&keyword={keyword.format(' ', '%20')}&os=windows&priority_region=&referer=&region=IE&screen_height=1440&screen_width=3440&tz_name=Europe%2FDublin&webcast_language=en"
    headers = {}

    if not util.exists(util.MEDUSA_PATH + "videos"):
        util.mkdir(util.MEDUSA_PATH + "videos")

    if not jobs.should_continue_thread(current_thread):
        jobs.medusa_job_print(f"Job '{keyword}': Thread killed")
        return

    sess = Session()

    sess.headers.update({'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"})
    sess.headers.update({'Accept-Language': 'en,en-US;q=0,5'})
    sess.headers.update({'Accept-Encoding': 'gzip, deflate'})
    sess.headers.update({'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'})
    sess.headers.update({'Upgrade-Insecure-Requests': '1'})

    if not jobs.should_continue_thread(current_thread):
        return

    data = None
    driver = None
    cookies = None

    if not jobs.should_continue_thread(current_thread):
        jobs.medusa_job_print(f"Job '{keyword}': Thread killed")
        return

    tiktok_cookies = util.medusa_get_setting("tiktok_cookies")[0]
    cookies = json.loads(tiktok_cookies)
    proxy = None

    if util.medusa_has_setting("proxies_enabled"):

        proxy = dr.medusa_get_random_proxy()

        jobs.medusa_job_print(f"{proxy} -> '{keyword}'")

    jobs.medusa_job_print(f"[{keyword}]: Gathering keyword data..")

    if not jobs.should_continue_thread(current_thread):
        return

    bs = medusa_proc_go_to_search(False, keyword, proxy)

    temp = bs

    find = temp.find('href="/')

    _links = []

    while find != -1:

        _start = find+7
        _link = temp[_start:]
        _end = _link.find('"')
        _link = _link[:_end]

        _links.append(_link)

        temp = temp[_start+_end+15:]

        find = temp.find('href="/')

    del _links[len(_links)-1]

    if not jobs.should_continue_thread(current_thread):
        return

    _links = list(dict.fromkeys(_links))
    _links = _links[-10:]

    if not jobs.should_continue_thread(current_thread):
        return

    for account in _links:

            profile_name = account

            if not jobs.should_continue_thread(current_thread):
                return

            jobs.medusa_job_print(f"Profile: {profile_name}")
            next_thread = len(util.MEDUSA_THREADS)+1

            x = util.threading.Thread(target=medusa_proc_tiktok_helper_download_all_videos,
                                 args=(profile_name, keyword,))
            x.do_run = True
            x.child_thread = False
            setattr(x, "child_thread", False)
            setattr(x, "done", False)
            setattr(x, "parent_thread", False)
            setattr(x, 'job_id', next_thread)
            x.start()

            if not jobs.should_continue_thread(current_thread):
                return

            util.MEDUSA_THREADS.append(x)

    jobs.medusa_job_print(f"Finished Controller job")

    try:
        jobs.medusa_kill_job(current_thread)
    except ValueError:
        pass


def medusa_proc_tiktok_helper_download_all_videos(profile_name, keyword=""):
    """
    Downloads TikTok videos from a given profile, filtered by an optional keyword
    Parameters:
    - profile_name (str or iterable): Name of the TikTok profile.
    - keyword (str, optional): Keyword to filter videos. Default is empty string.
    """

    util.sleep(0.4)

    current_thread = util.threading.current_thread()

    try:
        getattr(current_thread, "done")
    except AttributeError:
        setattr(current_thread, "done", 0)
        setattr(current_thread, "failed", 0)

    if type(profile_name) != "string":
        profile_name = ''.join(profile_name)

    if profile_name[0] != '@':
        profile_name = '@' + profile_name

    if type(keyword) != "string":
        keyword = ''.join(keyword)

    headers = {}
    cookies = None

    if not jobs.should_continue_thread(current_thread):
        jobs.medusa_job_print(f"{profile_name}: Thread killed")
        return

    tiktok_cookies = util.medusa_get_setting("tiktok_cookies")[0]
    cookies = json.loads(tiktok_cookies)

    c = {c['name']:c['value'] for c in cookies}

    url = f"https://www.tiktok.com/{profile_name}?lang=en"

    jobs.medusa_job_print(f"Profile link: {url}..\n")

    if not jobs.should_continue_thread(current_thread):
        jobs.medusa_job_print(f"{profile_name}: Thread killed")
        return

    if len(keyword) == 0:
        if not util.exists(util.MEDUSA_PATH + "profiles"):
            util.mkdir(util.MEDUSA_PATH + f"profiles")
            jobs.medusa_job_print("Profiles directory created..")
        else:

            if not util.exists(f"profiles/{profile_name}"):

                util.mkdir(util.MEDUSA_PATH + 'profiles/' + profile_name)
                jobs.medusa_job_print("User directory created..")
    else:
        if not util.exists(util.MEDUSA_PATH + "keywords"):
            util.mkdir(util.MEDUSA_PATH + "keywords")
            jobs.medusa_job_print("Keywords directory created..")

        if not util.exists(util.MEDUSA_PATH + "keywords/" + keyword):
            util.mkdir(util.MEDUSA_PATH + "keywords/" + keyword)
            jobs.medusa_job_print("Category directory created..")

    if not jobs.should_continue_thread(current_thread):
        return

    jobs.medusa_job_print("Creating session headers..")

    sess = Session()

    sess.headers.update({'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"})
    sess.headers.update({'Accept-Language': 'en,en-US;q=0,5'})
    sess.headers.update({'Accept-Encoding': 'gzip, deflate'})
    sess.headers.update({'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'})
    sess.headers.update({'Upgrade-Insecure-Requests': '1'})

    if not jobs.should_continue_thread(current_thread):
        return

    date = None
    bs = ""

    proxy = None

    if util.medusa_has_setting("proxies_enabled") and util.medusa_has_setting("rotate_proxy"):

        proxy = dr.medusa_get_random_proxy()

        proxies = {
            "http": proxy,
        }

        jobs.medusa_job_print(f"Using proxy {proxy}")

    driver = dr.medusa_get_driver(False, "", proxy, True, "normal", True)

    jobs.medusa_job_print(f"Getting {profile_name}'s videos..")

    try:
        driver.get(url)

        while "tiktok-yvmafn-DivVideoFeedV2 ecyq5ls0" not in driver.page_source:
            pass


        util.sleep(1)

    except WebDriverException:
        jobs.medusa_job_print("Tunnel connection failed, possible error with proxy? Ending job..")
        jobs.medusa_kill_job(current_thread, "Tunnel connection failure")
        return

    if util.medusa_has_setting("extended_search"):

        for i in range(35):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            util.sleep(0.1)
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
            util.sleep(0.2)

    video_links = []

    if util.medusa_has_setting("extended_search"):
        src = driver.page_source

        driver.close()

        soup = BeautifulSoup(src, "html.parser").decode()

        find_video = soup.find(f"{profile_name}/video/")

        while find_video != -1:

            temp = soup[find_video:]

            end_quote = temp.find('"')

            video = soup[find_video:find_video+end_quote]

            last_id = video.rfind("/")
            last_id = video[-last_id+1:]

            last_id = last_id.replace("lang=en", "")
            last_id = last_id.replace("vid/", "")
            last_id = last_id.replace("/", "")
            last_id = last_id.replace("d/", "")
            last_id = last_id.replace("id/", "")
            last_id = last_id.replace("deo", "")
            last_id = last_id.replace("eo", "")
            last_id = last_id.replace("o", "")
            last_id = last_id.replace("d", "")
            last_id = last_id.replace("vi", "")

            last_id = last_id.replace("*", "")
            last_id = last_id.replace("\\", "")
            last_id = last_id.replace("\\\\", "")
            last_id = last_id.replace("/", "")
            last_id = last_id.replace('"', "")
            last_id = last_id.replace("?", "")
            last_id = last_id.replace(">", "")
            last_id = last_id.replace("<", "")
            last_id = last_id.replace("|", "")
            last_id = last_id.replace("  ", "")

            jobs.medusa_job_print(f"Found video {last_id}")

            video_links.append(video)

            soup = soup[find_video+end_quote+1:]

            find_video = soup.find(f"{profile_name}/video/")

    else:
        src = driver.page_source

        driver.close()

        soup = BeautifulSoup(src, "html.parser").decode()

        user_post = soup.rfind('user-post')

        soup = soup[user_post:]

        _next = soup.find("[")
        _end = soup.find("]")

        soup = soup[_next:_end] + ']'
        soup = soup.split(",")

        for item in soup:
            item = item.replace('"', "")
            item = item.replace('[', '')
            item = item.replace(']', '')

            last_id = item

            last_id = last_id.replace("lang=en", "")
            last_id = last_id.replace("vid/", "")
            last_id = last_id.replace("/", "")
            last_id = last_id.replace("d/", "")
            last_id = last_id.replace("id/", "")
            last_id = last_id.replace("deo", "")
            last_id = last_id.replace("eo", "")
            last_id = last_id.replace("o", "")
            last_id = last_id.replace("d", "")
            last_id = last_id.replace("vi", "")

            last_id = last_id.replace("*", "")
            last_id = last_id.replace("\\", "")
            last_id = last_id.replace("\\\\", "")
            last_id = last_id.replace("/", "")
            last_id = last_id.replace('"', "")
            last_id = last_id.replace("?", "")
            last_id = last_id.replace(">", "")
            last_id = last_id.replace("<", "")
            last_id = last_id.replace("|", "")
            last_id = last_id.replace("  ", "")

            new_str = f"http://tiktok.com/{profile_name}/video/{last_id}"

            video_links.append(new_str)

    if not jobs.should_continue_thread(current_thread):
        return

    if len(video_links) == 0:
        jobs.medusa_kill_job(current_thread, "No videos found :(")
        return

    jobs.medusa_job_print(f"Starting {len(video_links)} jobs")

    if not jobs.should_continue_thread(current_thread):
        return

    total_threads = 0

    for key, link in enumerate(video_links):

        next_thread = len(util.MEDUSA_THREADS)

        if len(util.MEDUSA_THREADS) < util.MEDUSA_MAX_JOBS:
            x = util.threading.Thread(target=medusa_proc_tiktok_helper_download_specific_video, args=(profile_name, sess.headers, c, link, keyword,))
            x.do_run = True
            setattr(x, "child_thread", True)
            setattr(x, "done", False)
            setattr(x, "parent_thread", current_thread)
            x.child_thread = True
            x.start()

            util.MEDUSA_THREADS.append(x)
            total_threads = total_threads + 1

            jobs.medusa_add_linked_thread(current_thread, x)

            util.sleep(0.1)

        else:

            x = util.threading.Thread(target=medusa_proc_tiktok_helper_download_specific_video, args=(profile_name, sess.headers, c, link, keyword,))
            setattr(x, "child_thread", True)
            setattr(x, "parent_thread", current_thread)
            x.child_thread = True
            x.do_run = False

            util.MEDUSA_JOBS_QUEUE.append(x)

            total_threads = total_threads + 1
            jobs.medusa_add_linked_thread(current_thread, x)

            util.sleep(0.1)

    while jobs.medusa_has_linked_threads(current_thread):
        num_running = 0
        num_idle = 0
        num_done = 0
        num_failed = 0

        try:
            num_done = getattr(current_thread, "done")
            num_failed = getattr(current_thread, "failed")
        except AttributeError:
            pass

        controlling = 0
        linked_threads = jobs.medusa_get_linked_threads(current_thread)

        for _thread in linked_threads:
            if getattr(_thread, "do_run"):
                num_running += 1
            else:
                num_idle += 1

        controlling = num_running + num_idle

        progress = float(num_done) / total_threads
        arrow = '=' * int(round(progress * 50) - 1) + '>'
        spaces = ' ' * (50 - len(arrow))
        stats = (f"Active: {num_running} | "
                 f"Idle: {num_idle} | "
                 f"Done: {num_done} | "
                 f"Failed: {num_failed} | "
                 f"Total: {total_threads}")

        jobs.medusa_job_print(profile_name)
        jobs.medusa_job_print(f'\rProgress: [{arrow + spaces}] {int(progress * 100)}% | {stats}\n')

        util.sleep(2)

    util.medusa_print("Finished Controller job")


def medusa_proc_tiktok_helper_download_specific_video(profile_name, headers, cookies, link, keywords="", timeouts=0, ignore=False):
    """
    Downloads a specific TikTok video from the provided link.

    Parameters:
    - profile_name (str): TikTok profile name.
    - headers (dict): Headers for the request.
    - cookies (dict): Cookies for the request.
    - link (str): Specific TikTok video link to download.
    - keywords (str, optional): Keywords for filtering. Defaults to an empty string.
    - timeouts (int, optional): Maximum time to wait for a response. Defaults to 0.
    - ignore (bool, optional): Flag to determine if the function should ignore certain conditions. Defaults to False.

    Returns:
    None. The video is saved locally based on the defined path in the function.
    """
    
    current_thread = util.threading.current_thread()
    video_id = ""
    video_handle = None
    path_file = ""

    if not jobs.should_continue_thread(current_thread):
        jobs.medusa_job_print(f"Video '{link}': Thread killed")
        return

    video_handle = None

    link = link[link.rfind("/")+1:]

    link_url = f"https://api2.musical.ly/aweme/v1/feed/?aweme_id={link}&version_code=262&app_name=musical_ly&channel=App&device_id=null&os_version=14.4.2&device_platform=iphone&device_type=iPhone9"

    data = None

    if not jobs.should_continue_thread(current_thread):
        jobs.medusa_job_print(f"Video '{link}': Thread killed")
        return

    if util.medusa_has_setting("proxies_enabled") and util.medusa_has_setting("rotate_proxy"):
        # rotate proxies

        proxy = ""

        while True:

            try:

                proxy = dr.medusa_get_random_proxy()

                proxies = {
                    "http": proxy,
                }

                data = get(url=link_url, headers=headers, cookies=cookies, proxies=proxies, timeout=2)

                if '"aweme_list"' in data.text:
                    break

            except:
                jobs.medusa_job_print(f"{proxy} -> problems with proxy, rotating..")
                pass
    else:
        # no rotation

        while True:
            data = get(url=link_url, headers=headers, cookies=cookies)

            if '"aweme_list"' in data.text:
                break

    if not jobs.should_continue_thread(current_thread):
        jobs.medusa_job_print(f"[{video_id}]: Thread killed by parent")
        return

    bs = BeautifulSoup(data.content, "html.parser").decode()

    if not jobs.should_continue_thread(current_thread):
        jobs.medusa_job_print(f"[{video_id}]: Thread killed by parent")
        return

    if "play_addr" in bs:

        video_id = link[link.rfind("/") + 1:]

        title_data = ""

        if not jobs.should_continue_thread(current_thread):
            jobs.medusa_job_print(f"[{video_id}]: Thread killed by parent")
            return

        if util.medusa_has_setting("download_by_caption"): # by caption
            _get_desc = bs.find('"desc":')
            _find = bs[_get_desc+8:]
            _find2 = _find.find('"')
            _find = _find[:_find2]
            title_data = _find

            if len(keywords) == 0:

                if len(title_data) == 0:
                    title_data = video_id

                if util.exists(util.MEDUSA_PATH + f"profiles/{profile_name}/{title_data}.mp4") and not ignore:

                    if util.getsize(util.MEDUSA_PATH + f"profiles/{profile_name}/{title_data}.mp4") > 0:
                        jobs.medusa_kill_job(current_thread, "Thread killed", 1)
                        return
                    else:
                        try:
                            util.remove(util.MEDUSA_PATH + f"profiles/{profile_name}/{title_data}.mp4")
                        except PermissionError:
                            pass
            else:

                if len(title_data) == 0:
                    title_data = video_id

                    if util.exists(util.MEDUSA_PATH + f"keywords/{keywords}/{title_data}.mp4") and not ignore:

                        if util.getsize(util.MEDUSA_PATH + f"keywords/{keywords}/{title_data}.mp4") > 0:
                            jobs.medusa_kill_job(current_thread, "Thread killed", 1)
                            return
                        else:
                            util.remove(util.MEDUSA_PATH + f"keywords/{keywords}/{title_data}.mp4")

        else: # by id now
            if len(keywords) == 0:
                if util.exists(util.MEDUSA_PATH + f"profiles/{profile_name}/{video_id}.mp4") and not ignore:

                    if util.getsize(util.MEDUSA_PATH + f"profiles/{profile_name}/{video_id}.mp4") > 0:
                        jobs.medusa_kill_job(current_thread, "Thread killed", 1)
                        return
                    else:
                        util.remove(util.MEDUSA_PATH + f"profiles/{profile_name}/{video_id}.mp4")
            else:
                if util.exists(util.MEDUSA_PATH + f"keywords/{keywords}/{video_id}.mp4") and not ignore:

                    if util.getsize(util.MEDUSA_PATH + f"keywords/{keywords}/{video_id}.mp4") > 0:
                        jobs.medusa_kill_job(current_thread, "Thread killed", 1)
                        return
                    else:
                        util.remove(util.MEDUSA_PATH + f"keywords/{keywords}/{video_id}.mp4")

        if not jobs.should_continue_thread(current_thread):
            jobs.medusa_job_print(f"[{video_id}]: Thread killed by parent")
            return

        bs = bs[bs.find("play_addr"):]

        url_list = bs.find("url_list")

        bs = bs[url_list+12:]

        _quote = bs.find('"')

        video_link = bs[:_quote]

        if not jobs.should_continue_thread(current_thread):
            return

        if util.medusa_has_setting("proxies_enabled") and util.medusa_has_setting("rotate_proxy"):

            if not jobs.should_continue_thread(current_thread):
                return

            proxy = ""

            while True:

                try:

                    proxy = dr.medusa_get_random_proxy()

                    proxies = {
                        "http": proxy,
                    }

                    jobs.medusa_job_print(f"{proxy} -> Video '{link}'")

                    data = get(url=video_link, cookies=cookies, headers=headers, proxies=proxies, timeout=2, stream=True)

                    if not jobs.should_continue_thread(current_thread):
                        return

                    break

                except:
                    jobs.medusa_job_print(f"{proxy} -> problems with proxy, rotating..")
                    pass

        else:
            data = get(video_link, headers=headers, cookies=cookies, stream=True)

        total_len = int(data.headers['Content-Length'])
        total_count = 0
        path_file = ""

        if not jobs.should_continue_thread(current_thread):
            return

        _temp = ""
        title_data = title_data.replace("*", "")
        title_data = title_data.replace("\\", "")
        title_data = title_data.replace("\\\\", "")
        title_data = title_data.replace("  ", "")

        if len(keywords) == 0:
        # not a keyword download
            if util.medusa_has_setting("download_by_caption"):

                if len(title_data) == 0:
                    title_data = video_id
                else:
                    if len(title_data) >= 12:
                        _temp2 = title_data
                        _temp = ""
                        title_data = title_data.split(" ")

                        for _str in title_data:
                            if len(_str) > 0 and _str[0] != '#':
                                del _str

                        if len(title_data) == 0:
                            title_data = _temp2.split(" ")

                            if len(title_data) > 6:
                                for i in range(6, len(title_data)-1):
                                    del title_data[i]

                        if len(title_data ) > 6:
                            for key, _str in enumerate(title_data):
                                if key > 6:
                                    del title_data[key]

                        for key, _str in enumerate(title_data):
                            if key > 0:
                                _temp += " "

                            _temp += _str

                        title_data = _temp

                    title_data = title_data

                title_data = title_data.replace("*", "")
                title_data = title_data.replace("\\", "")
                title_data = title_data.replace("\\\\", "")
                title_data = title_data.replace("/", "")
                title_data = title_data.replace('"', "")
                title_data = title_data.replace("?", "")
                title_data = title_data.replace(">", "")
                title_data = title_data.replace("<", "")
                title_data = title_data.replace("|", "")
                title_data = title_data.replace("  ", "")

                path_file = util.MEDUSA_PATH + f"profiles/{profile_name}/{title_data}.mp4"
                try:
                    video_handle = open(path_file, "wb")
                except FileNotFoundError:
                    if video_handle is not None:
                        video_handle.close()

                    jobs.medusa_kill_job(current_thread, "Could not open file")
                    return

            else:
                path_file = util.MEDUSA_PATH + f"profiles/{profile_name}/{video_id}.mp4"

                try:
                    video_handle = open(path_file, "wb")
                except FileNotFoundError:
                    if video_handle is not None:
                        video_handle.close()

                    jobs.medusa_kill_job(current_thread, "Could not open file")
                    return
        else:
            # it is a keyword download
            video_id = link[link.rfind("/") + 1:]

            if util.medusa_has_setting("download_by_caption") and len(title_data) > 0:
                # download keyword by caption
                if len(title_data) == 0:
                    title_data = video_id
                else:
                    if len(title_data) > 12:
                        title_data = title_data[:-5]

                jobs.medusa_job_print(f"[{video_id}]: Downloading by caption: '{title_data}'")

                title_data = title_data[:15]
                title_data = title_data.replace("*", "")
                title_data = title_data.replace("\\", "")
                title_data = title_data.replace("\\\\", "")
                title_data = title_data.replace("/", "")
                title_data = title_data.replace('"', "")
                title_data = title_data.replace("?", "")
                title_data = title_data.replace(">", "")
                title_data = title_data.replace("<", "")
                title_data = title_data.replace("|", "")
                title_data = title_data.replace("  ", "")

                path_file = util.MEDUSA_PATH + f"keywords/{keywords}/{title_data}.mp4"

                try:
                    video_handle = open(path_file, "wb")
                except FileNotFoundError:
                    if video_handle is not None:
                        video_handle.close()

                    jobs.medusa_kill_job(current_thread, "Could not open file")
                    return

            else:
                # download keyword by video id
                jobs.medusa_job_print(f"[{video_id}]: Downloading by video id")

                path_file = util.MEDUSA_PATH + f"keywords/{keywords}/{video_id}.mp4"
                video_handle = open(path_file, "wb")

            if not jobs.should_continue_thread(current_thread):
                video_handle.close()
                return

    else:
        medusa_proc_tiktok_helper_download_specific_video(profile_name, headers, cookies, link, keywords, timeouts, True)
        jobs.medusa_job_print(f"[{profile_name}]: Could not retrieve video, retrying..")
        return

    if type(util.MEDUSA_CHUNK_SIZE) == "list":
        util.MEDUSA_CHUNK_SIZE = util.MEDUSA_CHUNK_SIZE[0][0]

    try:
        for chunk in data.iter_content(chunk_size=util.MEDUSA_CHUNK_SIZE): # 1048576 max

            if not jobs.should_continue_thread(current_thread):
                video_handle.close()
                return

            if chunk:
                total_count += util.MEDUSA_CHUNK_SIZE
                video_handle.write(chunk)

    except ConnectionError:
        video_handle.close()
        medusa_proc_tiktok_helper_download_specific_video(profile_name, headers, cookies, link, keywords, timeouts)
        jobs.medusa_job_print(f"Connection closed from proxy, retrying..")
        return

    video_handle.close()
    jobs.medusa_kill_job(current_thread, "job completed", 1)


def medusa_proc_post_handle_caption(file, driver):
    """Handle the caption setting for the video."""

    try:
        caption_field = driver.find_element(By.XPATH, "//*[contains(@class, 'editorContainer')]/div")
        if file.replace(".mp4", "").isnumeric():
            _rand = "#tiktok #love #like #follow #memes #explorepage ..."
            caption_field.send_keys(_rand)
        else:
            caption_field.send_keys(file.replace(".mp4", ""))
    except WebDriverException:
        pass


def medusa_proc_post_upload_video(post_from, file, driver):
    """Handle the video uploading process."""

    print(post_from, file)
    for _ in range(20):
        try:
            file_input_element = driver.find_element(By.XPATH, '//*[contains(@class, "jsx-2751257330")]/input')
            print(file_input_element)
            if post_from not in file_input_element.get_attribute("innerHTML"):
                file_input_element.send_keys(post_from + file)
            break
        except:
            pass


def medusa_proc_post_video(file, driver, current_thread, profile_dir, proxy, post_from, single):
    """Handle the video posting process after upload."""

    try:
        post_btn = driver.find_element(By.XPATH, "//button[not(@disabled)]/div/div[text()='Post']")
        post_btn.click()
    except NoSuchElementException:
        pass


def initialize_driver(profile_dir, proxy, headless=True):
    """
    Initializes a new web driver with the given configurations.

    Args:
        profile_dir (str): The directory path containing the user profile.
        proxy (str): The proxy address to use. If set to "any" or "*", a random proxy will be selected.
        headless (bool, optional): Whether to run the browser in headless mode. Defaults to True.

    Returns:
        driver: The initialized web driver instance.
    """

    if proxy in ["any", "*"]:
        proxy = dr.medusa_get_random_proxy()
    return dr.medusa_get_driver(True, profile_dir, proxy, headless, "normal")


def handle_post_from_path(post_from):
    """
    Processes the provided path to make it compatible with the application's expected format.

    Args:
        post_from (str): Initial directory or file path.

    Returns:
        str: Modified and processed path.
    """

    _t = list("ABCDEFGHIJKLMNOP")
    if post_from[0] not in _t and post_from[1] != ':':
        post_from = util.MEDUSA_PATH + post_from
    return post_from.replace("\\", "/").rstrip('/') + '/'


def wait_for_element(driver, by, value, timeout):
    """
     Waits until a specified element is located on the web page.

     Args:
         driver: The web driver instance.
         by: The method to locate the element.
         value: The specific value to use with the locating method.
         timeout (int): The number of seconds to wait before giving up.

     Returns:
         bool: True if the element is found within the timeout, False otherwise.
     """

    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value)))
        return True
    except:
        return False


def handle_iframe_failure(driver, message):
    """
    Handles failures related to iframe interactions, quits the driver, and stops the job.

    Args:
        driver: The web driver instance.
        message (str): Message to be printed.
    """

    util.medusa_print(message)
    util.medusa_print("Please try again or recreate Account")
    jobs.medusa_kill_job(util.threading.current_thread())
    driver.quit()


def verify_click_post_btn(driver):
    """
     Attempts to click the post button on a page, while handling various potential issues.

     Args:
         driver: The web driver instance.

     Returns:
         tuple: A tuple containing a boolean indicating success, and a message in case of failure.
     """

    tries = 5

    while tries > 0:
        try:
            post_btn = driver.find_element(By.XPATH, "//button[not(@disabled)]/div/div[text()='Post']")
            post_btn.click()
            break
        except NoSuchElementException:
            tries -= 1
            util.sleep(1)

    if tries <= 0:
        return False

    tries = 5

    span_elements = driver.find_elements(By.TAG_NAME, "span")
    while tries > 0:
        if len(span_elements) > 20:
            return False, "'Too Many Uploads' received"
        else:
            tries -= 1
            util.sleep(1)

    tries = 5

    while tries > 0:
        if "Drag the slider" in driver.page_source:
            return False, "Captcha encountered"  # Captcha triggered
        else:
            tries -= 1
            util.sleep(1)

    return True


def find_upload_element(driver):
    """
    Tries to find an upload input element on a page.

    Args:
        driver: The web driver instance.

    Returns:
        bool: True if the element is found, False otherwise.
    """

    try:
        file_input_element = driver.find_element(By.XPATH,
                                                 '//*[contains(@class, "jsx-2404389384 ")]/input')

        if file_input_element:
            return True

    except:
        return False


def get_post_driver(profile_dir, proxy):
    """
    Initializes and returns a web driver instance based on provided parameters and user settings.

    Args:
        profile_dir (str): The directory path containing the user profile.
        proxy (str): The proxy to be used with the web driver.

    Returns:
        driver: The initialized web driver instance.
    """

    driver = None

    if util.medusa_has_setting("proxies_enabled"):
        headless = util.medusa_has_setting("enable_headless")
        driver = initialize_driver(profile_dir, proxy, headless)
    else:
        headless = util.medusa_has_setting("enable_headless")
        driver = dr.medusa_get_driver(True, profile_dir, None, headless, "normal")

    return driver


def medusa_proc_handle_single_upload(driver, files, profile_dir, proxy, post_from, completed, single):
    """
    Handles the process of uploading a single video to TikTok.

    Args:
        driver: The web driver instance.
        files (list): The file list to upload from.
        profile_dir (str): The directory path containing the user profile.
        proxy (str): The proxy to be used with the web driver.
        post_from (str): The directory path from which to retrieve videos to post.
        completed (list): A list to track the files that have been successfully uploaded.
        single (bool): Determines if only a single video should be posted.

    Returns:
        None
    """

    current_thread = util.threading.current_thread()

    to_del = ""
    completed_file = ""

    try:
        found = wait_for_element(driver, By.TAG_NAME, "iframe", 20)

        if not found:
            util.medusa_print("Could not get iframe - not logged in?")
            util.medusa_print("Please try again or recreate Account")
            jobs.medusa_kill_job(current_thread)
            return

        util.sleep(4)

    except TimeoutException:
        util.medusa_print("Unable to post video - timeout? Retrying with any proxy")
        driver.quit()
        medusa_proc_post_tiktok(profile_dir, "any", post_from, single)
        return

    except UnexpectedAlertPresentException:
        jobs.medusa_job_print("Unable to post video - timeout? Retrying with any proxy")
        driver.quit()
        medusa_proc_post_tiktok(profile_dir, "any", post_from, single)
        return

    driver.switch_to.frame(0)
    driver.implicitly_wait(1)

    file = util.choice([f for f in files if f not in completed])

    completed_already = file in completed

    if not jobs.should_continue_thread(current_thread):
        if driver is not None:
            driver.quit()
        return

    if not completed_already:
        medusa_proc_post_handle_caption(file, driver)
        jobs.medusa_job_print(f"Uploading video '{file}'")
        medusa_proc_post_upload_video(post_from, file, driver)

        post_btn = None
        util.sleep(1)

        found = find_upload_element(driver)

        if not jobs.should_continue_thread(current_thread):
            if driver is not None:
                driver.quit()
            return

        if found:
            util.medusa_print("Could not upload video - timeout? Retrying..")

            if driver is not None:
                driver.quit()

            medusa_proc_post_tiktok(profile_dir, proxy, post_from, single)
            return

        found = False

        while not found:
            try:
                post_btn = driver.find_element(By.XPATH, "//button[not(@disabled)]/div/div[text()='Post']")
                found = True
            except NoSuchElementException:
                pass

        jobs.medusa_job_print(f"Posting video '{file}'")

        util.sleep(2)

        if not jobs.should_continue_thread(current_thread):
            if driver is not None:
                driver.quit()
            return

        success, msg = verify_click_post_btn(driver)

        if not success:
            jobs.medusa_job_print(f"Posting failed! {msg}")
            driver.quit()
            jobs.medusa_kill_job(current_thread)
            return

    # TODO: Check we are done uploading
    util.sleep(10)

    if util.medusa_has_setting("delete_once_uploaded"):
        if util.exists(post_from + file):
            to_del = post_from + file
            completed_file = file
            jobs.medusa_job_print(f"Completed file upload '{completed_file}'")
            util.remove(to_del)
            completed.append(completed_file)

    if single:
        jobs.medusa_job_print("Upload finished - killing job")
        driver.quit()
        jobs.medusa_kill_job(current_thread)
        return

    driver.refresh()


def medusa_proc_post_tiktok(profile_dir, proxy, post_from, single=False):
    """
    Automates the process of posting videos to TikTok using a web driver.

    Args:
        profile_dir (str): The directory path containing the user profile.
        proxy (str): The proxy to be used with the web driver.
        post_from (str): The directory path from which to retrieve videos to post.
        single (bool, optional): Determines if only a single video should be posted. Defaults to False.

    Returns:
        None
    """

    current_thread = util.threading.current_thread()
    tiktok_upload_url = "https://www.tiktok.com/upload?lang=en"

    driver = None

    if not jobs.should_continue_thread(current_thread):
        return

    driver = get_post_driver(profile_dir, proxy)

    for i in range(15):
        try:
            driver.minimize_window()
        except WebDriverException:
            util.medusa_print("Please click Chrome notifications before continuing!")
            util.sleep(5)

    if not jobs.should_continue_thread(current_thread):
        driver.quit()
        return

    # Handle post_from
    post_from = handle_post_from_path(post_from)

    try:
        files = util.listdir(post_from)
    except FileNotFoundError:
        util.medusa_print("Cannot find directory '" + post_from + "'!")
        return

    completed = []

    if not jobs.should_continue_thread(current_thread):
        driver.quit()
        return

    jobs.medusa_job_print(f"Moving to upload page..")

    driver.get(tiktok_upload_url)

    jobs.medusa_job_print(f"Waiting for iframe")

    util.sleep(4)

    dr.medusa_scroll_window(driver, 5)

    if not medusa_proc_handle_single_upload(driver, files, profile_dir, proxy, post_from, completed, single):
        return


def medusa_proc_tiktok_gather_cookies(driver):
    """
    Specialized function to retrieve cookies from TikTok by navigating
    to random user search until a specific element is found.

    Args:
        driver: Web driver instance.
    """

    found = False
    tries = 10

    util.sleep(3)

    while not found and tries > 0:
        try:
            dr.medusa_find_element_by_xpath(driver, "p", "tiktok-1v1eqb4-PTitle e10wilco4")
            found = True
        except NoSuchElementException:
            random_word = util.medusa_get_random_word(6)
            driver.get(f"https://www.tiktok.com/search/user?q={random_word}")
            util.sleep(4)
            tries -= 1

        if found:
            return True

        return False


def medusa_proc_goto_and_save_header_cookies(driver, name, url):
    """
    Navigate to a specific URL, wait for a specified element to appear,
    grab cookies, save them, and then close the browser.

    Args:
        driver: Web driver instance.
        name: Name of the platform/website (e.g., "tiktok").
        url: URL to navigate to.

    Returns:
        headers: Dictionary of request headers (currently empty in the provided code).
        req_cookies: Dictionary of cookies.
    """

    util.medusa_print("We just have to grab some cookies first..")
    util.medusa_print("This can take up to a minute, please be patient")

    req_cookies = {}

    if name == "tiktok":

        gathered_cookies = medusa_proc_tiktok_gather_cookies(driver)

        if not gathered_cookies:
            util.medusa_print("Could not gather cookies!")
            driver.close()
            return {}, []

    cookies = driver.get_cookies()
    headers = {}

    for cookie in cookies:
        req_cookies[cookie["name"]] = cookie["value"]

    num_entries = len(util.MEDUSA_DATA_SAVES)
    util.MEDUSA_DATA_SAVES[num_entries] = {
        "name": name,
        "cookies": req_cookies
    }

    util.medusa_save_data(name, headers, req_cookies)

    driver.close()

    return headers, req_cookies


def _kill_target_job_and_linked_threads():
    """
    Kill the target job specified by MEDUSA_JOB_VIEW and its linked threads if they exist.
    """

    target_thread = util.MEDUSA_THREADS[util.MEDUSA_JOB_VIEW]

    if jobs.medusa_has_linked_threads(target_thread):

        linked_threads = jobs.medusa_get_linked_threads(target_thread)

        for thread in linked_threads:
            # Attempt to kill the child thread
            _attempt_kill_job(thread, "Killed by parent")

    # Attempt to kill the target thread
    _attempt_kill_job(target_thread, "Killed by user")


def _attempt_kill_job(thread, message):
    """
    Attempt to kill the specified job thread with a given message.

    Args:
        thread: The thread/job to kill.
        message: Reason message for killing the job.
    """

    try:
        jobs.medusa_kill_job(thread, message)
    except ValueError:
        pass


def medusa_proc_view_job():
    """
    Display a menu to the user to manage jobs. The current functionality allows killing a job.
    """

    showing = False

    menu = "\n\t\t\t1. Kill Job"

    print(menu)

    _input = util.medusa_input("")

    if _input == 1:
        _kill_target_job_and_linked_threads()


def _display_accounts():
    accounts = util.medusa_get_setting("accounts")

    for key, entry in enumerate(accounts):
        profile_name = entry[0]
        proxy_type = entry[1]
        profile_dir = entry[2]

        util.medusa_print(f"Account {str(key + 1)}:\n\t Account {profile_name}\n\t Proxy: {proxy_type}\n\t"
                          f" Directory: {profile_dir}\n")


def _get_account_details(account_post):
    """
    Retrieve the profile directory and proxy details for the selected account.
    """
    accounts = util.medusa_get_setting("accounts")
    account_post = int(account_post) - 1
    for key, entry in enumerate(accounts):

        if key == account_post:
            return entry[2], entry[1]

    return None, None


def _initiate_upload(profile_dir, proxy):
    """
    Initiate the upload process either directly or with multiple upload jobs based on settings.
    """
    post_from = util.medusa_str_input("Please enter directory to post from (n to cancel): ")
    upload_num = _get_upload_num_setting()

    if post_from != 'n':
        jobs.medusa_job_print("Beginning upload job..\n")

        if upload_num is None:
            _start_thread(medusa_proc_post_tiktok, profile_dir, proxy, post_from)
        else:
            _start_multiple_threads(upload_num, profile_dir, proxy, post_from)


def _start_thread(target_function, *args):
    """
    Start a single thread for uploading.
    """
    x = util.threading.Thread(target=target_function, args=args)
    x.do_run = True
    setattr(x, "child_thread", False)
    setattr(x, "parent_thread", False)
    setattr(x, "done", False)
    x.start()
    util.MEDUSA_THREADS.append(x)


def _start_multiple_threads(upload_num, profile_dir, proxy, post_from):
    """
    Start multiple threads for uploading.
    """
    temp = ""

    for i in range(upload_num):
        if proxy:
            temp, proxy = proxy, dr.medusa_get_random_proxy()

        _start_thread(medusa_proc_post_tiktok, profile_dir, proxy, post_from, True)

        if temp:
            proxy, temp = temp, ""


def _get_upload_num_setting():
    """
    Retrieve the upload number setting if it exists.
    """
    if util.medusa_has_setting("upload_num") and util.medusa_has_setting("enable_multiupload"):
        _upload = util.medusa_get_setting("upload_num")[0]
        return _upload[0] if isinstance(_upload, list) else _upload
    return None


def medusa_proc_posting():
    """
     Handles the posting process
     """

    # Check if accounts are set up
    if util.medusa_has_setting("accounts") and len(util.medusa_get_setting("accounts")) >= 1:

        _display_accounts()
        account_post = util.medusa_str_input("Please enter account to post from or 'n' to cancel: ")

        if account_post != 'n':

            profile_dir, proxy = _get_account_details(account_post)

            if profile_dir:

                post_from = util.medusa_str_input("Please enter directory to post from (n to cancel): ")
                upload_num = _get_upload_num_setting()

                if post_from != 'n':

                    jobs.medusa_job_print("Beginning upload job..\n")

                    if upload_num is None:
                        _start_thread(medusa_proc_post_tiktok, profile_dir, proxy, post_from)
                    else:
                        _start_multiple_threads(upload_num, profile_dir, proxy, post_from)
            else:
                util.medusa_print("There was an issue gathering account details!")
    else:
        util.medusa_print("You need to setup an Account first!")
        util.medusa_print("Please go to Settings -> Accounts -> Add Account")


def medusa_proc_go_to_search(cookies_enabled=False, keyword="", proxy=None):
    """
    Navigate to TikTok search using a web driver.

    Parameters:
    - cookies_enabled (bool): Whether to enable cookies or not.
    - keyword (str): Search keyword for TikTok.
    - proxy (str): Proxy details.

    Returns:
    - BeautifulSoup object if cookies are not enabled.
    """

    driver = None
    use_cookies = not cookies_enabled

    if proxy is None:
        driver = dr.medusa_get_driver(False, "", None, use_cookies, "normal", True)
    else:
        driver = dr.medusa_get_driver(False, "", proxy, use_cookies, "normal", True)

    while True:

        random_word = util.medusa_get_random_word(5)

        # Update search URL depending on cookies_enabled variable
        search_url = f"https://www.tiktok.com/search/user?q={random_word}" if cookies_enabled else f"https://www.tiktok.com/search/user?q={keyword}"

        driver.get(search_url)
        util.medusa_print(f"-> {search_url}")

        # Delay for 5 seconds to allow page to load
        util.sleep(5)

        _exit = False
        _body = driver.execute_script("return document.body.innerHTML;")

        page_source = driver.page_source

        num_a_elements = driver.find_elements(By.TAG_NAME, "a")

        if len(num_a_elements) > 30:
            break

    # Handle cookies if they are enabled
    if cookies_enabled:
        cookies = driver.get_cookies()
        driver.quit()
        util.medusa_add_setting("tiktok_cookies", json.dumps(cookies))
        util.medusa_print("Cookies saved!")
    else:
        bs = BeautifulSoup(driver.page_source, "html.parser").decode()
        driver.quit()
        return bs


def medusa_add_procedure(name, func):
    """Add a new procedure to MEDUSA_PROCEDURE."""

    num_proc = len(util.MEDUSA_PROCEDURE)

    util.MEDUSA_PROCEDURE[num_proc] = {'name': name, 'proc': func}


def medusa_has_procedure(name):
    """Check if a procedure with a given name exists in MEDUSA_PROCEDURE.

    Special handling for 'view_job_' prefixes. For such names, the function sets
    the global MEDUSA_JOB_VIEW and returns True, 0.

    Args:
        name (str): The name of the procedure.

    Returns:
        tuple: A tuple containing a boolean indicating if the procedure exists and
        an index (or -1 if not found).
    """

    num_proc = len(util.MEDUSA_PROCEDURE)
    proc_index = 0

    if num_proc <= 0:
        return False, -1

    if "view_job_" in name:

        job_id = int(name.replace("view_job_", ""))
        util.MEDUSA_JOB_VIEW = job_id

        return True, 0

    for i in range(num_proc):

        if util.MEDUSA_PROCEDURE[i]['name'] == name:
            return True, i

    return False, -1


def medusa_load_procedure(index):
    """Load and execute a procedure based on its index."""

    util.MEDUSA_PROCEDURE[index]['proc']()


def medusa_set_maximum_threads():
    """Set the maximum number of threads (or jobs) for the application."""

    max_jobs = int(input("Please enter maximum running jobs: "))

    util.MEDUSA_MAX_JOBS = max_jobs

    if util.medusa_has_setting("max_jobs"):
        util.medusa_set_setting("max_jobs", [max_jobs])
    else:
        util.medusa_add_setting("max_jobs", [max_jobs])


medusa_add_procedure("view_job", medusa_proc_view_job)
medusa_add_procedure("tiktok_download_by_name", medusa_proc_tiktok_download_by_name)
medusa_add_procedure("tiktok_download_by_keyword", medusa_proc_tiktok_download_by_keyword)
medusa_add_procedure("tiktok_posting", medusa_proc_posting)
medusa_add_procedure("set_maximum_threads", medusa_set_maximum_threads)