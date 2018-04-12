import logging
import glob
import os

from time import localtime, strftime

def pruneLogs(logDirectory):
	logFileInfo = [ ]
	for logFile in glob.glob(logDirectory + "/*.log.txt"):
		logFileInfo.append([os.path.getctime(logFile), logFile])
	for logToDelete in sorted(logFileInfo)[:-2]:
		os.remove(logToDelete[1])

def setupLogging(logDirectory):
	timeStr = strftime("rpi.%Hh_%Mm.log.txt", localtime())
	logFormat = '%(asctime)s - (%(module)s:%(lineno)d) %(message)s'
	if logDirectory:
		logfile = logDirectory + "/" + timeStr
		logging.basicConfig(filename=logfile, filemode="w", level=logging.DEBUG, format = logFormat)
	else:
		logging.basicConfig(level=logging.DEBUG, format = logFormat)
