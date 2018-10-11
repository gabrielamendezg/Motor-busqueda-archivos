"""
	"MOTOR DE BUSQUEDA DE ARCHIVOS"
"""
import os
import re

INSTRUCTIVO = "\tINSTRUCCIONES:\n\tEscriba el modo seguido de los terminos que desea buscar\n\tPresione Enter para salir.\n\tMODOS DE BUSQUEDA:\n\tAND: Se listarán los archivos que coinciden con todos los términos.\n\tNOT: Se listarán los archivos que no coincidan con el término\n\tOR: Se listaran los archivos que coinciden con algún término\n\t*Puede omitirse el comando 'OR/or:' para realizar este tipo de busqueda\n"
OR = "or"
AND = "and"
NOT = "not"
MODOS = (OR,AND,NOT)
FORMATOS = (".txt",".py",".md",".c")
PRIMER_TERMINO = 1
MODO = 0
NOMBRE_ARCH = 2

def main():
	"""
    Función principal del programa. Ofrece una línea de comandos interactiva,
    pide al usuario una entrada de terminos de busqueda para buscar archivos 
    dentro del directorio actual, según el modo que se le especifique imprime 
    por pantalla las rutas a los archivos que correspondientes.
    Este proceso se repite hasta que el usuario ingrese "Enter" (cadena vacía).
    """
	try:
		directorio=indexar()
		indice=crear_indice(directorio)
		print(INSTRUCTIVO)
		busqueda=input("> ")
		resultado=[]
		while busqueda:
			terminos_busq=re.split('\W+',busqueda.lower())
			modo_busq=modo(terminos_busq)
			if modo_busq==AND:
				resultado=busqueda_and(terminos_busq,indice)
			elif modo_busq==NOT:
				if len(terminos_busq)>2:
					print("Debe ingresarse un único término para este modo")
				else:
					resultado=busqueda_not(terminos_busq,indice)
			else:
				resultado=busqueda_or(terminos_busq,indice)
		
			if resultado:
				for ruta in resultado:
					print(ruta)
			else:
				print("No hay coincidencias")
			busqueda=input("> ")
	except OSError:
		print("Problema indexando archivos")

"""----------------------------------------------------------"""

def es_texto(direccion):
	"""
	Recibe una cadena con una ruta válida a un archivo existente
	Devuelve True si el archivo es un texto, caso contrario False. 
	"""
	for formato in FORMATOS:
		if direccion.endswith(formato):
			return True
	return False

"""----------------------------------------------------------"""

def indexar():
	"""
	Lee las rutas de los archivos en la carpeta actual.
	Salida por pantalla informando el proceso en acción y la cantidad
	de archivos indexados.
	Devuelve una lista con las rutas de todos los archivos.
	"""
	print("Indexando archivos...")
	directorio=[]
	contador_arch=0   #contador de archivos indexados.
	for root,dirs,archivos in os.walk("."):
		for nombre in archivos:
			contador_arch+=1
			directorio.append(str(os.path.join(root,nombre)))
	print("Listo! {} archivos indexados".format(contador_arch))
	return directorio

"""----------------------------------------------------------"""

def crear_indice(directorio):
	"""
	Recibe una lista de cadenas con rutas a archivos válidas.
	Devuelve un diccionario a manera de "Indice invertido",
	donde las claves son los terminos en los archivos o sus nombres y los
	valores son las rutas donde se encontró dicho termino.
	"""
	indice={}
	for direccion in directorio:
			agregar_a_indice(indice,direccion,direccion)
			if es_texto(direccion):
				try:
					with open(direccion[NOMBRE_ARCH:]) as archivo:
						for linea in archivo:
							agregar_a_indice(indice,linea,direccion)
				except: 
					print("Algo salió mal con el archivo {}".format(direccion[NOMBRE_ARCH:]))
					continue
	return indice

"""----------------------------------------------------------"""

def agregar_a_indice(diccionario,texto,valor):
	"""
	Recibe un diccionario, una cadena de texto y un valor a asignar a cada
	término del texto en el diccionario. Modifica el diccionario agregando
	los términos del texto que no se encontraban en este con el respectivo
	valor pasado por parametro en una lista, de encontrarse en el diccionario, 
	se añade el valor a la lista de valores del término."""

	terminos=re.split('\W+',texto.lower())
	for termino in terminos:
		if not termino in diccionario:
			diccionario[termino]=[valor]
		else:
			diccionario[termino].append(valor)


def modo(terminos):
	"""
	Recibe una lista con los terminos de la cadena de busqueda.
	De haberse ingresado un modo de busqueda, devuelve dicho valor, 
	de no haberse ingresado uno, por default devuelve "or"
	"""
	modo=terminos[MODO]	#contiene el modo ingresado de haberse especificado.
	if modo in MODOS:
			return modo
	return OR

"""----------------------------------------------------------"""

def busqueda_and(busqueda,indice):
	"""
	Recibe una lista con los terminos de busqueda y un diccionario 
	de los terminos en los archivos y sus direcciones. Devuelve una 
	lista con las direcciones que contienen todos los terminos de busqueda.
	"""
	rutas=[]
	terminos_en_busqueda=len(busqueda)
	num_palabras=terminos_en_busqueda-1			#Ignora el comando "and"
	for termino in range(PRIMER_TERMINO,terminos_en_busqueda):
		if not busqueda[termino] in indice:
			return []
	diccionario={}
	for termino in range(PRIMER_TERMINO,terminos_en_busqueda):
		for direccion in indice[busqueda[termino]]:
			if direccion in diccionario:
				diccionario[direccion]+=1
			else:
				diccionario[direccion]=1
	for ruta,contador in diccionario.items():
		if contador==num_palabras:
			rutas.append(ruta)
	return rutas

"""----------------------------------------------------------"""

def busqueda_not(busqueda,indice):
	"""
	Recibe una lista con los terminos de la cadena de busqueda y 
	un diccionario de los terminos en los archivos y sus direcciones. 
	Devuelve una lista con las direcciones que no contienen el termino de busqueda.
	"""
	rutas=[]
	termino=busqueda[PRIMER_TERMINO]
	for palabra,direcciones in indice.items():
			for direccion in direcciones: 
				if not direccion in rutas and not direccion in indice[termino]:
					rutas.append(direccion)
	return rutas

"""----------------------------------------------------------"""

def busqueda_or(busqueda,indice):
	"""
	Recibe una lista con los terminos de busqueda y un diccionario de 
	los terminos en los archivos y sus direcciones. Devuelve una lista 
	con las direcciones que contienen alguno de los terminos de busqueda.
	"""
	rutas=[]
	for termino in busqueda:
		if termino in indice:
			for direccion in indice[termino]:
				if not direccion in rutas:
					rutas.append(direccion)
	return rutas

"""----------------------------------------------------------"""

main()
