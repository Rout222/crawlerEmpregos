import urllib.request, json
from urllib.request import urlopen,build_opener
from bs4 import BeautifulSoup, element
from math import floor
import threading
import time
processados = 0
threadLock = threading.Lock()
inicio = time.time()
class trabalhabrasil(threading.Thread):
	origem 	= "http://www.trabalhabrasil.com.br/{}"
	urlbase = "https://www.trabalhabrasil.com.br/api/v1.0/Job/List?idFuncao=0&idCidade=0&pagina={}&pesquisa=&ordenacao=1&idUsuario="

	"""docstring for trabalhabrasil"""
	def __init__(self, nThreads, inicio):
		super(trabalhabrasil, self).__init__()
		self.nThreads = nThreads
		self.inicio = inicio
		self.falhou = False

	def run(self):
		print("Startando thread {}".format(self.inicio))
		self.comecar()

	def comecar(self):
		self.pag = 2 + self.inicio 
		while(True):
			self.pag += self.nThreads
			with urllib.request.urlopen(self.urlbase.format(self.pag)) as url:
				    data = json.loads(url.read().decode())
				    for link in data:
			    		self.vaga(self.origem.format(link["u"]))


	def vaga(self, url):
		global processados
		opener = build_opener()
		opener.addheaders = [('User-Agent', 'Mozilla/5.0')]

		while(not self.falhou):
			try:
				request = opener.open(url, timeout = 5)
			except Exception as e:
				self.falhou = True
			else:
				self.falhou = False

		html = BeautifulSoup(request, "html.parser")
		nome = html.select(".job-title")[0].text.strip()
		divdados = html.select(".job-text")[0]
		for x in divdados.children:
			if type(x) is element.Tag:
				if(x.text.strip() == "Salário:"):
					salario = x.nextSibling.nextSibling.text.split('-')[0].strip()
				if(x.text.strip() == "Cidade/Estado:"):
					cidade = x.nextSibling.nextSibling.text.strip()
				if(x.text.strip() == "Descrição:"):
					descricao = x.nextSibling.nextSibling.text.strip()
		threadLock.acquire()
		processados += 1
		threadLock.release()
		
numThreads = 3
threads = []
i = 0
for x in range(numThreads): # cria as threads
	threads.append(trabalhabrasil(numThreads, i))
	i += 1

for x in threads: # starta as threads
	x.start()

while(True):
	time.sleep(10)
	tempo = time.time() - inicio
	threadLock.acquire()
	p = processados
	threadLock.release()
	print("Processo iniciado à {}s, média de inserção de {} vagas por segundo".format(floor(tempo), round(p/tempo,2)))

		