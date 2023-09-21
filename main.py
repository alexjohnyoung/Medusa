import util
import proc
import jobs
import menu


def main():
    abs_pth = util.abspath(util.argv[0])
    your_dir = util.dirname(abs_pth)

    util.MEDUSA_PATH = your_dir.replace("\\", "/") + '/'
    util.MEDUSA_EXE = abs_pth.replace("\\", "/")

    util.system('color')
    util.system('title Medusa')

    num_saves = util.medusa_load_data_saves()

    util.medusa_load_settings()

    if not util.medusa_has_setting("jobs_show"):
        util.medusa_add_setting("jobs_show", [1])

    if not util.medusa_has_setting("tiktok_cookies"):
        util.medusa_print("Just getting some cookies real quick..")
        proc.medusa_proc_go_to_search(True)

    if util.medusa_has_setting("max_jobs"):
        util.MEDUSA_MAX_JOBS = util.medusa_get_setting("max_jobs")[0]

    if util.medusa_has_setting("chunk_size"):
        util.MEDUSA_CHUNK_SIZE = util.medusa_get_setting("chunk_size")[0]

    if type(util.MEDUSA_CHUNK_SIZE) == "list":
        util.MEDUSA_CHUNK_SIZE = util.MEDUSA_CHUNK_SIZE[0]

    x = util.threading.Thread(target=jobs.medusa_jobs_handle_queue)
    x.do_run = True
    x.start()

    menu.medusa_show_page("main_menu")


if __name__ == "__main__":
    main()
