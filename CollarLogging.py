import logging

from time import localtime, strftime

def setupLogging(logDirectory):
	timeStr = strftime("%mm_%dd_%Hh_%Mm_%Ss", localtime())
	logFormat = '%(asctime)s - (%(module)s:%(lineno)d) %(message)s'
	if logDirectory:
		logfile = logDirectory + "/" + "collar.log." + timeStr
		logging.basicConfig(filename=logfile, filemode="w", level=logging.DEBUG, format = logFormat)
	else:
		logging.basicConfig(level=logging.DEBUG, format = logFormat)
