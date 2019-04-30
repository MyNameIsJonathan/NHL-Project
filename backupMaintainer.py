from glob import glob
import pandas as pd
from os import remove


def cleanupBackups():

    """
    Removes old backup pickle files of the NHL_Database tables (pickled pandas
        DataFrames)

        Keeps:
            All backups for the past week
            All backups from the 1st and 15th of each month

        Deletes:
            All others

    Args:
        None

    Returns:
        None

    Raises:
        None
    """

    # Create the timestamps for the days' backups to keep
    today = pd.to_datetime('today').date()
    oneWeekAgo = today - pd.Timedelta(weeks=1)

    # Create a list of dates for which the backups will be kept
    myDatesToKeep = pd.date_range(start=oneWeekAgo, end=today)

    # Get the filenames of all pickled backups in the folder
    allBackups = glob("/NHL-Project/mysqlbackups/*.pickle")

    # Keep only wanted backups
    backupsToKeep = []
    for i in allBackups:
        myDate = pd.to_datetime(i, format="/NHL-Project/mysqlbackups/backup_%Y-%m-%d.pickle").date()
        if (myDate in myDatesToKeep) or (myDate.day == 1) or (myDate.day == 15):
            backupsToKeep.append(i)

    # Remove unwanted files
    for i in allBackups:
        if not i in backupsToKeep:
            remove(i)
