#!/usr/bin/python
#-----------------------------------------------------------------------------
# Descripcion: Analiza log generado por ffmpeg del script sdi_analyzer.sh y
#              y genera un file con los logs de eventos observados.
# Modo de ejecucion:
#   sudo python start_sdi_monitor_0_1.py -h  para ayuda.
# Autor: JCRAMIREZ
# Fecha Modificacion: 28 DIC 2016
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
# Global Variable
#****************************************************************************
logs_path = "/home/user/sdi_monitor/logs"


#****************************************************************************
# Funtions
#****************************************************************************

def open_log_file():
	#crea o abre archivo del dia, entregando el apuntador.
	# file_path = expanduser("~") + "/sdi_monitor/logs"
	file_path = logs_path
	if not os.path.exists(file_path):
		os.makedirs(file_path)
	
	today = datetime.datetime.now()
	today_strg = "%.2i_%.2i_%.2i" % (today.year, today.month, today.day)
	file_name = "sdi_monitor_" + today_strg + ".log"
	
	file = os.path.join(file_path,file_name)
	file_pointer = open(file, 'a')
	return(file_pointer)


def print_log_file(file_pointer, print_log_line):
	#Imprime la linea en entrada con un salto de line al final.
	file_pointer.write(print_log_line + "\r\n")


def close_log_file(file_pointer):
	#Cierra el archivo que ingresa el aputador.
	if file_pointer is not None:
		file_pointer.close()


def date_hour_now():
	#Entrega la cadena de fecha y hora actual.
	now = datetime.datetime.now()
	now_strg = "%.2i-%.2i-%.2i %.2i:%.2i:%.2i" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
	return(now_strg)		


def log_line_now(channel, event):
	#Concatena la fecha y hora actual con el canal SDI
	log_msg = date_hour_now() + " - SDI CHANNEL " + channel + " - " + event
	return(log_msg)


def event_to_file(event):
	#escribe los eventos un file almacenado
	file_out = open_log_file()
	print_log_file(file_out,event)
	close_log_file(file_out)


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


def readlines_then_tail(fin):
	#Iterate through lines and then tail for further lines."
	while True:
		line = fin.readline(500)
		if line:
			yield line
		else:
			tail(fin)


def tail(fin):
	#"Listen for new lines added to file."
	while True:
		where = fin.tell()
		line = fin.readline(200)
		if not line:
			fin.seek(where)
		else:
			yield line


def analiza_log_ffmpeg(file_ffmpeg, VERBOSE_MODE, BLACK_THOLD):
	#Carga los log generado por el processo FFMPEG
	with open(file_ffmpeg, 'r') as fin:
		blck_frame_seen1 = True      #Variable de control deteccion NEGRO
		count_frames_detected = 0    #Variable de control deteccion NEGRO  
		blck_detected = True 		 #Variable de control deteccion NEGRO   
		for line in readlines_then_tail(fin):
			# Detecta en logfile desconexion
			if "No input signal detected" in line:
				evento_msg = log_line_now("1","Disconnected")
				if VERBOSE_MODE:
					print evento_msg
				envio_email(evento_msg)
				event_to_file(evento_msg)
			# Detecta en logfile conexion
			if "Input returned" in line:
				evento_msg = log_line_now("1","Connected")
				if VERBOSE_MODE:
					print evento_msg
				envio_email(evento_msg)
				event_to_file(evento_msg)
			# Detecta NEGRO
			if "type" in line:
				if blck_frame_seen1:
						t = re.search("t:([0-9.]+)", line)
						if t:
							t0 = float(t.group(1))
							t1 = float(t.group(1))
						f = re.search("frame:([0-9.]+)", line)
						if f:
							f0 = float(f.group(1))
							f1 = float(f.group(1))
						blck_frame_seen1 = False
				else:
						f = re.search("frame:([0-9.]+)", line)
						if f:
							f1 = float(f.group(1))
						t = re.search("t:([0-9.]+)", line)
						if t:
							t1 = float(t.group(1))
						frame_diff = f1 - f0
						if frame_diff == 1:
								t = re.search("t:([0-9.]+)", line)
								if t:
									t_anterior = float(t.group(1))
								f0 = f1
								count_frames_detected += 1
								blck_duration = t_anterior - t0
								if (blck_duration > BLACK_THOLD) and blck_detected:   #HUMBRAL en segundos
									evento_msg = log_line_now("1","Black Detected")
									if VERBOSE_MODE:
										print evento_msg
									envio_email(evento_msg)
									event_to_file(evento_msg)
									blck_detected = False
						else:
								blck_frame_seen1 = True
								count_frames_detected = 0
								blck_detected = True
								t0 = t1
								f0 = f1
			# Entrega la duracion NEGRO
			b = re.search("black_duration:([0-9.]+)$", line)
			if b:
				duration = b.group(1)
				evento_msg = log_line_now("1","Black Duration: ") + duration + " segundos"
				if VERBOSE_MODE:
					print evento_msg
				envio_email(evento_msg)
				event_to_file(evento_msg)
			# Detecta silencio
			if "silence_start" in line:
				evento_msg = log_line_now("1","Silence Detected")
				if VERBOSE_MODE:
					print evento_msg
				envio_email(evento_msg)
				event_to_file(evento_msg)
			# Entrega la duracion del Silencio
			s = re.search("silence_duration: ([0-9.]+)$", line)
			if s:
				duration = s.group(1)
				evento_msg = log_line_now("1","Silence Duration: ") + duration + " segundos"
				if VERBOSE_MODE:
					print evento_msg
				envio_email(evento_msg)
				event_to_file(evento_msg)


def main():
	__author__ = 'jcramirez - jcramirez@rcntv.com.co'
	parser = argparse.ArgumentParser(description='Proceso para monitoreo y envio de alarmas por comportamiento de interfaz SDI')
	parser.add_argument('-v', '--verbose', action='store_true', help="Activa los logs en pantalla")
	parser.add_argument('-tb', type=int, default=5, help="Tiempo en segundos de humbral para deteccion de black frames (Default:5 segundos)")
	parser.add_argument('-tm', type=int, default=5, help="Tiempo en segundos de humbral para deteccion de silencios (Default:5 segundos)")
	args = parser.parse_args()

	#Eliminar los logs temporales de ffmpeg (ffmpeg_outx.log) si existen:
	subprocess.call("sudo rm -f /home/user/sdi_monitor/ffmpeg_out1.log", shell=True)

	#Corre el proceso ffmpeg que entregara los log del puerto SDI	
	cmd_ffmpeg = "nohup ffmpeg -nostats -hide_banner -f decklink  -i 'DeckLink SDI (1)@10' -vf 'blackdetect=d=" + str(args.tb) + ":pix_th=0.00,blackframe=100:32' -af 'silencedetect=n=-50dB:d=" + str(args.tm) + "' -f null - >> /home/user/sdi_monitor/ffmpeg_out1.log 2>&1 &"
	subprocess.call(cmd_ffmpeg, shell=True)
	time.sleep(1)
	
	#Analiza los log entregados por el proceso ffmpeg y analiza los eventos
	analiza_log_ffmpeg("/home/user/sdi_monitor/ffmpeg_out1.log", args.verbose, args.tb)

#****************************************************************************
# MAIN process
#****************************************************************************
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		try:
			subprocess.call("sudo rm -f /home/user/sdi_monitor/ffmpeg_out1.log", shell=True)
			sys.exit(0)	
		except SystemExit:
			os._exit(0)
	except:
		try:
			print "Revisar!....Errores al ejecutar proceso."
			subprocess.call("sudo killall ffmpeg", shell=True)
			subprocess.call("sudo rm -f /home/user/sdi_monitor/ffmpeg_out1.log", shell=True)
			sys.exit(0)	
		except SystemExit:
			os._exit(0)
