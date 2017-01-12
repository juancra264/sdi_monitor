#!/usr/bin/python
#----------------------------------------------------------------------------
# Descripcion:
#   Revisa cada minuto que el proceso ffmpeg asociado a un o varios
#   canales este funcionando. Sino reinicia el proceso basado en el
#   script de ffmpeg.
# Modo de ejecucion:
#   Se ejecuta por tiempo en un crontab cada minuto
#   crontab:
#		* * * * * python /home/user/enc_scripts/watchdog_ffmpeg.py
# Fecha Modificacion: 05 Ene 2017
# Autor: JCRAMIREZ
#----------------------------------------------------------------------------

#****************************************************************************
# Library Load
#****************************************************************************
import os
import sys
import time
import select
import traceback
import smtplib
import datetime
import argparse
import subprocess
import shlex

from subprocess import *
#***************************************************************************
# Global Variables
#***************************************************************************

#***************************************************************************
# Funtions
#************************************************************************** 


def envio_email(message_in):
	# envio de correo electronico a un smpt server
	now = datetime.datetime.now()
	now_strg = "%.2i-%.2i-%.2i %.2i:%.2i:%.2i" % (now.year,now.month,now.day,now.hour,now.minute,now.second)
	sender = 'sdi_monitor_1@rcntecnica.com'
	receivers = ['jcramirez@rcntv.com.co']
	server = "172.20.7.19"
	email_head = """From: sdi_monitor_1 <sdi_monitor_1@rcntecnica.com>\nTo: Juan Carlos Ramirez Angel <jcramirez@rcntv.com.co>\nSubject:Evento SDI_Monitor_1\n\n"""
	message = email_head + now_strg + "\n" + message_in + "\n"
	try:
		smtpObj = smtplib.SMTP(server)
		smtpObj.sendmail(sender, receivers, message)
		#print "Notificacion Enviada"
	except:
		print "No se envio notificacion"


def check_sdi_monitor():
	#Revisa Canal 1: Winsports Contribucion
	ffmpeg_pid = subprocess.Popen("""ps -ef | grep "DeckLink SDI (1)" | grep -v grep | awk '{print $2}'""", shell=True, stdout=subprocess.PIPE).stdout.read().rstrip()
	if not ffmpeg_pid.isdigit():
		subprocess.call('sudo python start_sdi_monitor_0_1.py &',shell=True,cwd='/home/user/sdi_monitor/')
		envio_email("Inicio de sdi_monitor: canal 1")
	return


def main():
	check_sdi_monitor()
	return

#****************************************************************************
#       MAIN
#****************************************************************************
if __name__ == '__main__':
	main()
