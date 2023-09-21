import util
import driver as dr
import proc


def medusa_show_page(menu_str):

    menu = ""
    menu_option = 1
    translation = []

    menu_str = "main_menu"
    util.MEDUSA_PAGE = "main_menu"

    while 0 < int(menu_option) < 8:

        util.medusa_logo()

        match util.MEDUSA_PAGE:

            # Main Menu
            case "main_menu": # first page
                menu = f"\t\t1. Download Videos\n\t\t2. Posting\n\t\t3. Jobs\n\t\t4. Settings"

                translation = [
                    [1, "tiktok_download_videos"],
                    [2, "tiktok_posting"],
                    [3, "jobs"],
                    [4, "settings"]
                ]

            # Jobs
            case "jobs":

                if len(util.MEDUSA_THREADS) == 0:
                    util.medusa_print("  No active threads running")
                    menu_str = "main_menu"
                else:

                    num_jobs = len(util.MEDUSA_THREADS)

                    menu = ""

                    menu += "\t\t0. Exit\n"

                    menu += "\t\t1. Kill All Jobs\n"

                    if util.medusa_has_setting("jobs_show"):
                        menu += "\t\t2. Hide Jobs\n\n"
                    else:
                        menu += "\t\t2. Show Jobs\n\n"

                    job_count = 2

                    translation = [
                        [1, "jobs_kill_all"],
                        [2, "jobs_show"]
                    ]

                    for key, thread in enumerate(util.MEDUSA_THREADS):

                        if not getattr(thread, "child_thread"):
                            job_count += 1
                            menu += f"\t\t{str(job_count)}. Job {str(key)}\n"
                            translation.append([job_count, f"view_job_{str(key)}"])

            # Settings
            case "settings":
                menu = "\t\t0. Exit\n"
                menu += "\t\t1. Threading\n"
                menu += "\t\t2. Proxies\n"
                menu += "\t\t3. Downloads\n"
                menu += "\t\t4. Accounts\n"
                menu += "\t\t5. Posting\n"

                translation = [
                    [1, "set_maximum_threads"],
                    [2, "proxies_page"],
                    [3, "downloads_settings"],
                    [4, "accounts_page"],
                    [5, "posting_page"]
                ]

            case "posting_page":
                menu = "\t\t0. Exit\n"

                if util.medusa_has_setting("enable_headless"):
                    menu += "\t\t1. Disable Headless\n"
                else:
                    menu += "\t\t1. Enable Headless\n"

                menu += "\t\t2. Set Upload Amount\n"
                menu += "\t\t3. Set Upload Delay\n"

                translation = [
                    [1, "toggle_post_headless"],
                    [2, "set_upload_amount"],
                    [3, "account_set_upload_delay"]
                ]

            case "toggle_post_headless":

                if util.medusa_has_setting("enable_headless"):
                    util.medusa_remove_setting("enable_headless")
                else:
                    util.medusa_add_setting("enable_headless", [1])

                medusa_show_page("main_menu")
                break

            case "toggle_multiupload":

                if util.medusa_has_setting("enable_multiupload"):
                    util.medusa_remove_setting("enable_multiupload")
                else:
                    util.medusa_add_setting("enable_multiupload", [1])

                medusa_show_page("main_menu")
                break

            case "set_upload_amount":
                amount = util.medusa_input("Please enter upload amount: ")

                if util.medusa_has_setting("upload_num"):
                    util.medusa_set_setting("upload_num", [amount])
                else:
                    util.medusa_add_setting("upload_num", [amount])

                medusa_show_page("main_menu")
                break

            case "downloads_settings":

                menu = "\t\t0. Exit\n"

                if util.medusa_has_setting("delete_once_uploaded"):
                    menu += "\t\t1. Disable Delete Once Uploaded\n"
                else:
                    menu += "\t\t1. Enable Delete Once Uploaded\n"

                if util.medusa_has_setting("extended_search"):
                    menu += "\t\t2. Disable Extended Search\n"
                else:
                    menu += "\t\t2. Enable Extended Search\n"

                menu += "\t\t3. Set Chunk Size\n"

                translation = [
                    [1, "toggle_delete_once_uploaded"],
                    [2, "toggle_extended_search"],
                    [3, "set_chunk_size"]
                ]

            case "toggle_extended_search":
                if util.medusa_has_setting("extended_search"):
                    util.medusa_remove_setting("extended_search")
                else:
                    util.medusa_add_setting("extended_search", [1])

                medusa_show_page("main_menu")
                break

            case "set_chunk_size":
                _inp = util.medusa_input("Please enter chunk size in MB: ")

                if util.medusa_has_setting("chunk_size"):
                    util.medusa_set_setting("chunk_size", [1000000 * _inp])
                else:
                    util.medusa_add_setting("chunk_size", [1000000 * _inp])

            case "toggle_delete_once_uploaded":

                if util.medusa_has_setting("delete_once_uploaded"):
                    util.medusa_remove_setting("delete_once_uploaded")
                else:
                    util.medusa_add_setting("delete_once_uploaded", [1])

                medusa_show_page("main_menu")
                break

            case "toggle_download_by_caption":

                if util.medusa_has_setting("download_by_caption"):
                    util.medusa_remove_setting("download_by_caption")
                else:
                    util.medusa_add_setting("download_by_caption", [1])

                menu_str = "main_menu"
                util.MEDUSA_PAGE = "main_menu"
                medusa_show_page("main_menu")
                break

            # Accounts
            case "accounts_page":

                menu = "\t\t0. Exit\n"
                menu += "\t\t1. Set Profile Directory\n"
                menu += "\t\t2. List Accounts\n"
                menu += "\t\t3. Add Account\n"
                menu += "\t\t4. Remove Account\n"
                menu += "\t\t5. Remove All Accounts"

                translation = [
                    [1, "account_set_directory"],
                    [2, "account_list"],
                    [3, "account_add"],
                    [4, "account_remove"],
                    [5, "account_remove_all"]
                ]

            case "account_set_upload_delay":

                _upd = util.medusa_input("Please enter upload delay in seconds: ")

                if util.medusa_has_setting("upload_delay"):
                    util.medusa_set_setting("upload_delay", [_upd])
                else:
                    util.medusa_add_setting("upload_delay", [_upd])

                medusa_show_page("main_menu")
                return

            case "account_remove":

                if util.exists("settings.txt"):
                    settings_handle = open(util.MEDUSA_PATH + "settings.txt", "r")
                    settings_data = settings_handle.read()
                    settings_handle.close()

                    if len(settings_data) > 0:

                        accounts = util.medusa_get_setting("accounts")
                        changed = False
                        proxy_list = []

                        for key, entry in enumerate(accounts):
                            profile_name = entry[0]
                            proxy_type = entry[1]
                            profile_dir = entry[2]

                            util.medusa_print(f"Account {str(key)}: Account {profile_name} -> proxy: {proxy_type}\n\t"
                                         f"Directory: {profile_dir}\n")

                    util.medusa_print("\n")

                    account_remove = util.medusa_input("Please enter account number you would like to remove: ")

                    _index = -1
                    _data = None

                    for key, entry in enumerate(util.MEDUSA_SETTINGS):
                        if util.MEDUSA_SETTINGS[entry]['name'] == 'accounts':
                            _index = entry

                            try:
                                _data = util.MEDUSA_SETTINGS[entry]['value'][int(account_remove)]
                            except IndexError:
                                medusa_show_page("main_menu")
                                return

                            break

                    if _index != -1:
                        _accountData = util.MEDUSA_SETTINGS[_index]['value']
                        _profileLocation = _accountData[int(account_remove)][2]

                        if util.exists(_profileLocation):
                            util.rmtree(_profileLocation, ignore_errors=True)

                        util.MEDUSA_SETTINGS[_index]['value'].remove(_data)
                        util.medusa_save_settings()

                medusa_show_page("main_menu")
                return

            case "account_remove_all":

                if util.exists("settings.txt"):
                    settings_handle = open(util.MEDUSA_PATH + "settings.txt", "r")
                    settings_data = settings_handle.read()
                    settings_handle.close()

                    if len(settings_data) > 0:
                        util.medusa_remove_setting("accounts")

                medusa_show_page("main_menu")
                return

            case "account_list":

                if util.medusa_has_setting("accounts"):

                    accounts = util.medusa_get_setting("accounts")

                    for key, entry in enumerate(accounts):
                        profile_name = entry[0]
                        proxy_type = entry[1]
                        profile_dir = entry[2]

                        util.medusa_print(f"Account {str(key+1)}:\n\t Account {profile_name}\n\t Proxy: {proxy_type}\n\t"
                                     f" Directory: {profile_dir}\n")

                medusa_show_page("main_menu")
                return

            case "account_set_directory":
                profile_dir = util.medusa_str_input("Please enter absolute path of Profile directory: ")

                if len(profile_dir) > 0:

                    if util.medusa_has_setting("profile_directory"):
                        util.medusa_set_setting("profile_directory", profile_dir)
                    else:
                        util.medusa_add_setting("profile_directory", profile_dir)

            case "account_add":

                proxy_no = None
                account_name = ""

                profile_name = util.medusa_str_input("Please enter name of account: ")
                has_path = util.medusa_has_setting("profile_directory")

                if util.medusa_has_setting("proxies"):
                    for key, entry in enumerate(util.medusa_get_setting("proxies")):
                        print(f"Proxy {str(key + 1)}: {entry}")

                    util.medusa_print("Please enter proxy to use for this account")
                    proxy_no = util.medusa_str_input("Or type 'any' to use any proxy: ")

                    if proxy_no != "any":
                        proxy_no = int(proxy_no) - 1

                        _proxies = util.medusa_get_setting("proxies")

                        for key, entry in enumerate(_proxies):
                            if key == proxy_no:
                                proxy_no = entry
                                break
                    else:
                        _ret = util.medusa_get_setting("proxies")
                        proxy_no = _ret[util.randint(0, len(_ret) - 1)]

                profile_path = ""

                if has_path:
                    profile_path = util.medusa_get_setting("profile_directory")[0]
                    profile_path = profile_path + '/' + profile_name
                else:
                    profile_path = "C:/temp/" + profile_name

                util.medusa_print("TikTok will now be opened in a separate browser")

                if proxy_no is None:
                    driver = dr.medusa_get_driver(True, profile_path)
                else:
                    print(proxy_no)
                    driver = dr.medusa_get_driver(True, profile_path, proxy_no)

                print(profile_path, proxy_no)
                driver.get("https://www.tiktok.com")

                done = util.medusa_str_input("Please login, save this information, click 'Accept Cookies' and type 'done'\n"
                                             "Please wait for the page to fully complete loading before typing this!\n")

                has_profile_dir = util.medusa_has_setting("profile_directory")
                profile_dir_location = ""

                if not has_profile_dir:
                    _dir = f"C:/temp"
                else:
                    _dir = "".join(util.medusa_get_setting("profile_directory")[0])

                if done != "done":

                    if util.exists(_dir + '/' + profile_name):
                        util.rmtree(_dir + '/' + profile_name, ignore_errors=True)
                else:

                    driver.refresh()

                    cookies = driver.get_cookies()

                    print(cookies)

                    util.medusa_add_setting("accounts", [profile_name, proxy_no, _dir + '/' + profile_name])
                    util.medusa_print("Account saved")

                driver.quit()
                medusa_show_page("main_menu")
                return

            case "proxies_page":

                translation = [
                    [1, "proxy_toggle"],
                    [2, "toggle_rotate_proxy"],
                    [3, "proxy_list"],
                    [4, "add_proxies"],
                    [5, "load_proxies"],
                    [6, "remove_proxies"],
                    [7, "remove_all_proxies"]
                ]
                menu = "\t\t0. Back\n"

                if not util.medusa_has_setting("proxies_enabled"):
                    menu += "\t\t1. Enable Proxies\n"
                else:
                    menu += "\t\t1. Disable Proxies\n"

                if not util.medusa_has_setting("rotate_proxy"):
                    menu += "\t\t2. Enable Proxy Rotation\n"
                else:
                    menu += "\t\t2. Disable Proxy Rotation\n"

                menu += "\t\t3. List Proxies\n"
                menu += "\t\t4. Add Proxies\n"
                menu += "\t\t5. Load Proxies from File\n"
                menu += "\t\t6. Remove Proxies\n"
                menu += "\t\t7. Remove All Proxies\n"

            case "proxy_list":

                if util.medusa_has_setting("proxies"):

                    proxies = util.medusa_get_setting("proxies")

                    if len(proxies) == 0:
                        return

                    for key, proxy in enumerate(proxies):
                        print(f"Proxy {key}: {proxy}\n")

            case "toggle_rotate_proxy":

                if util.medusa_has_setting("rotate_proxy"):
                    util.medusa_remove_setting("rotate_proxy")
                else:
                    util.medusa_add_setting("rotate_proxy", [1])

                medusa_show_page("main_menu")
                return

            case "remove_all_proxies":

                if util.exists("settings.txt"):
                    settings_handle = open(util.MEDUSA_PATH + "settings.txt", "r")
                    settings_data = settings_handle.read()
                    settings_handle.close()

                    if len(settings_data) > 0:
                        util.medusa_remove_setting("proxies")

                medusa_show_page("main_menu")
                return

            case "load_proxies":

                if not util.exists("load_proxy.txt"):
                    create_file = util.medusa_input("Please enter a list of your proxies into load_proxy.txt and press enter: ")

                if util.exists("load_proxy.txt"):

                    proxy_handle = open(util.MEDUSA_PATH + "load_proxy.txt", "r")
                    proxy_data = proxy_handle.read()
                    proxy_handle.close()

                    proxy_data = proxy_data.split("\n")

                    for proxy in proxy_data:
                        if type(proxy) != "str":
                            proxy = ''.join(proxy)

                        colon_count = 0

                        for char in proxy:
                            if char == ':':
                                colon_count += 1

                        if colon_count > 1:
                            proxy = proxy.split(":")

                            ip = proxy[0]
                            port = proxy[1]

                            user = proxy[2]
                            pw = proxy[3]

                            new_str = f"http://{user}:{pw}@{ip}:{port}"
                            proxy = new_str

                        util.medusa_add_setting("proxies", proxy)

                medusa_show_page("main_menu")
                return

            case "proxy_toggle":
                if util.medusa_has_setting("proxies_enabled"):
                    util.medusa_remove_setting("proxies_enabled")
                else:
                    util.medusa_add_setting("proxies_enabled", [1])

                medusa_show_page("main_menu")
                return

            case "add_proxies":

                _data = util.medusa_str_input("Please enter proxy details (ip:port): ")
                util.medusa_add_setting("proxies", _data)
                print("\033[H\033[J", end="")

                medusa_show_page("main_menu")
                return

            case "remove_proxies":

                if util.exists("settings.txt"):
                    settings_handle = open(util.MEDUSA_PATH + "settings.txt", "r")
                    settings_data = settings_handle.read()
                    settings_handle.close()

                    if len(settings_data) > 0:

                        settings_data = util.json.loads(settings_data)
                        changed = False
                        proxy_list = []

                        for key, entry in enumerate(settings_data):
                            if settings_data[entry]['name'] == 'proxies':
                                proxy_list = list(settings_data[entry]['value'])

                                for key, proxy in enumerate(proxy_list):
                                    print(f"Proxy {key}: {proxy}\n")

                                num_remove = int(util.medusa_input("Please enter proxy number to remove: "))

                                new_proxy_list = []

                                for key, proxy in enumerate(proxy_list):
                                    if key != num_remove:
                                        new_proxy_list.append(proxy)

                                util.medusa_set_setting("proxies", new_proxy_list)
                                break

                medusa_show_page("main_menu")
                return

            case "jobs_show":

                print("\033[H\033[J", end="")

                if util.medusa_has_setting("jobs_show"):
                    util.medusa_remove_setting("jobs_show")
                    util.medusa_print("Hiding jobs..")
                else:
                    util.medusa_add_setting("jobs_show", [1])
                    util.medusa_print("Showing jobs..")

                medusa_show_page("main_menu")
                return


            # TikTok Download Videos
            case "tiktok_download_videos":
                menu = f"\t\t0. Exit\n\t\t1. Download By Name\n\t\t2. Download By Keyword\n"

                translation = [
                    [1, "tiktok_download_by_name"],
                    [2, "tiktok_download_by_keyword"]
                ]

            case "tiktok_download_by_name":
                pass

            case "tiktok_download_by_keyword":
                pass

        print(menu)

        try:
            menu_option = util.medusa_no_prompt_input()
        except KeyboardInterrupt:
            pass

        if int(menu_option) == 0:

            menu_str = "main_menu"
            util.MEDUSA_PAGE = "main_menu"
            medusa_show_page("main_menu")
            return

        for translate in translation:
            try:
                if translate[0] == int(menu_option):
                    menu_str = translate[1]
            except ValueError:
                menu_str = "main_menu"
                util.MEDUSA_PAGE = menu_str
                medusa_show_page(menu_str)
                return

        proc_exists, proc_index = proc.medusa_has_procedure(menu_str)

        if proc_exists:
            proc.medusa_load_procedure(proc_index)
            menu_str = "main_menu"

        util.MEDUSA_PAGE = menu_str
