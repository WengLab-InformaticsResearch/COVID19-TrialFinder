# logging utlities

import logging

# logs on shell
def slogger (name):
    log = logging.getLogger (name)
    log.setLevel (logging.INFO)
    formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s', "%d-%m-%Y %H:%M:%S")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


# logs on file
def logger (name):
    log = logging.getLogger(name)
    log.setLevel (logging.INFO)
    formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s', "%d-%m-%Y %H:%M:%S")

    # info
    hfile_info = logging.FileHandler("C:/Users/butle/OneDrive/Documents/Columbia_Research Year/Weng Lab/Criteria2Query/covid_19/COVID_Trial_Finder-master/COVID_Trial_Finder-master/dquest-flask/app/log/dquest-info.log")
    hfile_info.setFormatter(formatter)
    hfile_info.setLevel(logging.INFO)
    log.addHandler(hfile_info)

    # error
    hfile_error = logging.FileHandler("C:/Users/butle/OneDrive/Documents/Columbia_Research Year/Weng Lab/Criteria2Query/covid_19/COVID_Trial_Finder-master/COVID_Trial_Finder-master/dquest-flask/app/log/dquest-error.log")
    hfile_error.setFormatter(formatter)
    hfile_error.setLevel(logging.ERROR)
    log.addHandler(hfile_error)
    # return
    return log


