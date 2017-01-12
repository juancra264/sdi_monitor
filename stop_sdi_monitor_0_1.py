#!/usr/bin/python
#-----------------------------------------------------------------------------
# Descripcion: Analiza log generado por ffmpeg del script sdi_analyzer.sh y
#              y genera un file con los logs de eventos observados.
# Modo de ejecucion:
#   sudo python start_sdi_monitor_0_1.py -h  para ayuda.
# Autor: JCRAMIREZ
# Fecha Modificacion: 04 ENE 2017
# Version 0.1
#-----------------------------------------------------------------------------

#*****************************************************************************
# Library Load
#*****************************************************************************
import time
import os
import re
import sys
import time
import select
import traceback
import smtplib
import datetime
import argparse
import subprocess
import shlex
from optparse import OptionParser
from os.path import expanduser

#****************************************************************************
# Funtions
#****************************************************************************


def envio_email(message_in):
	# envio de correo electronico a un smpt server
	sender = 'sdi_monitor_1@rcntecnica.com'
	receivers = ['jcramirez@rcntv.com.co']
	server = "172.20.7.19"
	email_head = """From: sdi_monitor_1 <sdi_monitor_1@rcntecnica.com>\nTo: Juan Carlos Ramirez Angel <jcramirez@rcntv.com.co>\nSubject:Evento SDI_Monitor_1\n\n"""
	message = email_head + message_in + "\n"
	try:
		smtpObj = smtplib.SMTP(server)
		smtpObj.sendmail(sender, receivers, message)
		#print "Notificacion Enviada"
	except:
		print "No se envio notificacion"


def main():
	__author__ = 'jcramirez - jcramirez@rcntv.com.co'
	parser = argparse.ArgumentParser(description='Proceso para monitoreo y envio de alarmas por comportamiento de interfaz SDI')
	parser.add_argument('-v', '--verbose', action='store_true', help="Activa los logs en pantalla")
	parser.add_argument('-tb', type=int, default=5, help="Tiempo en segundos de humbral para deteccion de black frames (Default:5 segundos)")
	parser.add_argument('-tm', type=int, default=5, help="Tiempo en segundos de humbral para deteccion de silencios (Default:5 segundos)")
	args = parser.parse_args()

	#Revisar la cantidad de processo ffmpeg corriendo
	pid = subprocess.Popen("""sudo ps -ef | grep "DeckLink SDI (1)" | grep -v grep | awk '{print $2}'""", stdout=subprocess.PIPE,shell=True).stdout.read().rstrip()
	if pid.isdigit():
		# Detiene
		cmd = "sudo kill -9 " + pid
		subprocess.call(cmd, shell=True)

	#Revisar la cantidad de processo python start_sdi_monitor
	pid = subprocess.Popen("""ps -ef | grep "python start_sdi_monitor_0_1" | grep -v grep | awk '{print $2}'""", shell=True, stdout=subprocess.PIPE).stdout.read().rstrip()
	if pid.isdigit():
		#Detiene los procesos start_sdi_monitor
		cmd = "sudo kill -9 " + pid
		subprocess.call(cmd, shell=True)

	#Eliminar los logs temporales de ffmpeg (ffmpeg_outx.log)
	subprocess.call("sudo rm -f /home/user/sdi_monitor/ffmpeg_out1.log", shell=True)

	#Termina todos los procesos python
	subprocess.call("sudo killall python", shell=True)

	print "SDI Monitor detenido correctamente!..."

#****************************************************************************
# MAIN process
#****************************************************************************
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		try:
			sys.exit(0)	
		except SystemExit:
			os._exit(0)
#	except:
#		try:
#			print "Revisar!....Errores al ejecutar proceso."
#			sys.exit(0)	
#		except SystemExit:
#			os._exit(0)
