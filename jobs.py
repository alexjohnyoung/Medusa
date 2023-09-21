import util


def medusa_jobs_handle_queue():
    """
    Continuously handles the job queue, launching threads if the number of running jobs is less than max jobs.
    """

    while True:

        if type(util.MEDUSA_MAX_JOBS) == "list":
            util.MEDUSA_MAX_JOBS = util.MEDUSA_MAX_JOBS[0]

            if type(util.MEDUSA_MAX_JOBS) == "list":
                util.MEDUSA_MAX_JOBS = util.MEDUSA_MAX_JOBS[0]

        num_running = 0

        for thread in util.MEDUSA_THREADS:

            if getattr(thread, "do_run"):
                num_running += 1

        if num_running < util.MEDUSA_MAX_JOBS and len(util.MEDUSA_JOBS_QUEUE) > 0:

            # Move in a thread from the queue

            rand = util.randint(0, len(util.MEDUSA_JOBS_QUEUE)-1)

            thread = util.MEDUSA_JOBS_QUEUE[rand]
            thread.do_run = True
            thread.start()

            util.MEDUSA_THREADS.append(thread)
            util.MEDUSA_JOBS_QUEUE.remove(thread)

            util.sleep(0.1)

        util.sleep(0.1)


def medusa_start_job(proc, args):

    next_thread = len(util.MEDUSA_THREADS)+1

    x = util.threading.Thread(target=proc, args=(args,))
    x.do_run = True
    x.child_thread = False
    setattr(x, "child_thread", False)
    setattr(x, "done", False)
    setattr(x, 'job_id', next_thread)
    x.start()

    util.MEDUSA_THREADS.append(x)

    util.medusa_print(f"Job started (job id: {str(next_thread)})\n")


def medusa_kill_job(current_thread, reason="job completed", success=0):

    index = util.MEDUSA_THREADS.index(current_thread)

    util.MEDUSA_THREADS[index].do_run = False

    util.MEDUSA_THREADS.remove(current_thread)

    found, entry = medusa_is_linked_thread(current_thread)

    if found:
        medusa_remove_linked_thread(current_thread, entry)

    parent_thread = getattr(current_thread, "parent_thread")

    if parent_thread is not None and parent_thread is not False:
        num_done = getattr(parent_thread, "done")
        num_failed = getattr(parent_thread, "failed")

        if success > 0:
            setattr(parent_thread, "done", num_done + 1)
        else:
            setattr(parent_thread, "failed", num_failed + 1)


def medusa_add_job_to_view(thread):

    util.MEDUSA_JOBS_LISTENING.append(thread)


def medusa_remove_job_from_view(thread):

    util.MEDUSA_JOBS_LISTENING.remove(thread)


def medusa_has_job_in_view(thread):

    return thread in util.MEDUSA_JOBS_LISTENING


def medusa_add_job_overview(parent_thread, txt):
    """
    Add a job to the overview with its corresponding text.

    Args:
    - parent_thread (Thread): The parent thread for the job.
    - txt (str): Text to associate with the job.
    """

    in_array = False
    _key = -1

    for key, entry in enumerate(util.MEDUSA_JOB_OVERVIEW):
        if entry[0] == parent_thread:
            in_array = True
            _key = key
            break

    if in_array:
        util.MEDUSA_JOB_OVERVIEW[_key] = txt
        return

    util.MEDUSA_JOB_OVERVIEW.append([parent_thread, txt])


def medusa_remove_job_overview(parent_thread):
    """
    Remove a specific job overview entry based on the given parent thread from the `MEDUSA_JOB_OVERVIEW` list.

    Args:
    - parent_thread (Thread): The parent thread whose job overview entry needs to be removed.

    Note:
    - If the specified parent thread is found in the `MEDUSA_JOB_OVERVIEW` list, its entry is removed.
      If it's not found, the function does nothing.
    """

    for key, entry in enumerate(util.MEDUSA_JOB_OVERVIEW):
        if entry[0] == parent_thread:
            del util.MEDUSA_JOB_OVERVIEW[key]
            return


def medusa_delete_job_overviews():
    """
    Remove all job overview entries from the `MEDUSA_JOB_OVERVIEW` list.

    Note:
    - This function will clear all entries in the `MEDUSA_JOB_OVERVIEW` list.
    """

    for key, entry in enumerate(util.MEDUSA_JOB_OVERVIEW):
        del util.MEDUSA_JOB_OVERVIEW[entry]


def medusa_has_linked_threads(parent_thread):
    """
    Check if the given parent thread has any linked threads in the `MEDUSA_LINKED_THREADS` dictionary.

    Args:
    - parent_thread (Thread): The parent thread to be checked.

    Returns:
    - bool: True if the parent thread has linked threads, False otherwise.

    Note:
    - This function searches the `MEDUSA_LINKED_THREADS` dictionary for the given parent thread and returns
      whether it is present as a parent thread in the dictionary.
    """

    for key, entry in enumerate(util.MEDUSA_LINKED_THREADS):

        parent = util.MEDUSA_LINKED_THREADS[entry]["parent_thread"]

        if parent == parent_thread:
            return True

    return False


def medusa_is_linked_thread(current_thread):
    """
    Determine whether a given thread is present in the global `MEDUSA_LINKED_THREADS` dictionary as either a
    linked thread or a parent thread. If the thread is a parent thread, it's also removed from the dictionary.

    Args:
    - current_thread (Thread): The thread to be checked.

    Returns:
    - tuple(bool, int): A tuple where the first element is a boolean that indicates if the thread was found.
                        The second element is the index of the entry in which the thread was found. If the thread
                        is not found, the second element is -1.

    Note:
    - The function interacts with the global `util.MEDUSA_LINKED_THREADS` dictionary.
    """

    found = -1

    for key, entry in enumerate(util.MEDUSA_LINKED_THREADS):
        linked_threads = util.MEDUSA_LINKED_THREADS[entry]['linked_threads']

        if current_thread in linked_threads:
            found = entry
            return True, found

    if found == -1:

        for key, entry in enumerate(util.MEDUSA_LINKED_THREADS):
            parent_thread = util.MEDUSA_LINKED_THREADS[entry]['parent_thread']

            if parent_thread == current_thread:
                found = entry

                del util.MEDUSA_LINKED_THREADS[entry]

                return True, found

    return False, -1


def medusa_get_linked_threads(parent_thread):
    """
    Retrieve the list of child or sub-job threads that are linked to a given parent thread.

    Args:
    - parent_thread (Thread): The parent thread object for which linked threads need to be fetched.

    Returns:
    - list[Thread]: A list of threads linked to the provided parent thread. If no linked threads are found,
                    returns None.

    Note:
    - This function interacts with the global `util.MEDUSA_LINKED_THREADS` dictionary to fetch the linked
      threads.
    """

    for key, entry in enumerate(util.MEDUSA_LINKED_THREADS):
        if util.MEDUSA_LINKED_THREADS[entry]['parent_thread'] == parent_thread:
            return util.MEDUSA_LINKED_THREADS[entry]['linked_threads']

    return None


def medusa_add_linked_thread(parent_thread, job_thread):
    """
    Link a job thread to a parent thread. If the parent thread does not already
    have an entry in MEDUSA_LINKED_THREADS, a new one is created.

    Args:
    - parent_thread (Thread): The thread object that represents the main or parent job.
    - job_thread (Thread): The thread object to be linked as a sub-job or child.

    Note:
    - The function interacts with the global `util.MEDUSA_LINKED_THREADS` dictionary
      to store and organize the relationship between parent and child threads.
    """

    index = -1

    if len(util.MEDUSA_LINKED_THREADS) > 0:
        for key, entry in enumerate(util.MEDUSA_LINKED_THREADS):
            if util.MEDUSA_LINKED_THREADS[entry]['parent_thread'] == parent_thread:
                index = entry
                break

    # If we found a thread
    if index > -1:

        num_linked_threads = len(util.MEDUSA_LINKED_THREADS[index]['linked_threads'])
        util.MEDUSA_LINKED_THREADS[index]['linked_threads'].append(job_thread)
    else:
        num_controllers = len(util.MEDUSA_LINKED_THREADS)

        util.MEDUSA_LINKED_THREADS[num_controllers] = {
            "parent_thread": parent_thread,
            "linked_threads": [job_thread]
        }


def should_continue_thread(thread):
    """Check if a thread should continue execution."""
    return getattr(thread, "do_run", False)

def medusa_remove_linked_thread(linked_thread, entry):
    """
    Remove a linked thread from the given entry. If there are no more linked threads
    under the specified entry, the entry itself is deleted.

    Args:
    - linked_thread (Thread): The thread object to be removed.
    - entry (int/str): The key for the entry in the MEDUSA_LINKED_THREADS dictionary.

    Note:
    - The function makes use of the global `util.MEDUSA_LINKED_THREADS` dictionary.
    """

    try:
        util.MEDUSA_LINKED_THREADS[entry]['linked_threads'].remove(linked_thread)
    except:
        pass

    if len(util.MEDUSA_LINKED_THREADS[entry]['linked_threads']) == 0:
        del util.MEDUSA_LINKED_THREADS[entry]


def medusa_job_print(txt):
    """
    Print a message with a specific prefix if the "jobs_show" setting is enabled.

    Args:
    - txt (str): The text message to print.
    """

    found = False

    if util.medusa_has_setting("jobs_show"):
        print("[" + util.Fore.RED + "Medusa" + util.Style.RESET_ALL + "]: " + txt)
