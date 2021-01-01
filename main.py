from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
from dateutil import tz
from threading import Thread

import json, sys, requests, configparser, csv, time, os


def banca():
	return API.get_balance()


def configuracao():
	arquivo = configparser.RawConfigParser()
	arquivo.read('config.txt')

	return {'entrada': arquivo.get('GERAL', 'entrada'), 'conta': arquivo.get('GERAL', 'conta'), 'stop_win': arquivo.get('GERAL', 'stop_win'), 'stop_loss': arquivo.get('GERAL', 'stop_loss'), 'payout': 0, 'banca_inicial': 0, 'martingale': arquivo.get('GERAL', 'martingale'), 'mgProxSinal': arquivo.get('GERAL', 'mgProxSinal'), 'valorGale': arquivo.get('GERAL', 'valorGale'), 'niveis': arquivo.get('GERAL', 'niveis'), 'analisarTendencia': arquivo.get('GERAL', 'analisarTendencia'), 'noticias': arquivo.get('GERAL', 'noticias'), 'hitVela': arquivo.get('GERAL', 'hitVela'), 'telegram_token': arquivo.get('telegram', 'telegram_token'), 'telegram_id': arquivo.get('telegram', 'telegram_id'), 'usar_bot': arquivo.get('telegram', 'usar_bot'), 'email': arquivo.get('CONTA', 'email'), 'senha': arquivo.get('CONTA', 'senha')}


def Clear_Screen():
	sistema = os.name
	if sistema == 'nt':
		os.system('cls')
	else:
		os.system('clear')


config = configuracao()
email = config['email']
senha = config['senha']
print('=========================================\n|             BOT SINAIS 2.0            |\n=========================================')
print('>> Conectando..\n')
API = IQ_Option(email, senha)

config = configuracao()
global galeRepete, lucroTotal, parAntigo, direcaoAntigo, timeframeAntigo, valor_entrada, galeSinalRepete, proxSinal
galeRepete = False
parAntigo = ''
direcaoAntigo = ''
timeframeAntigo = ''
lucroTotal = 0
valorGaleProxSinal = config['entrada']
valor_entrada = config['entrada']
analisarTendencia = config['analisarTendencia']
galeVela = config['mgProxSinal']
galeSinal = config['martingale']
noticias = config['noticias']
hitdeVela = config['hitVela']

global VERIFICA_BOT, TELEGRAM_ID
VERIFICA_BOT = config['usar_bot']
TELEGRAM_ID = config['telegram_id']


def Mensagem(mensagem, enviar_telegram=False):
	print(mensagem)
	if enviar_telegram == True and VERIFICA_BOT == 'S':
		token = config['telegram_token']
		chatID = TELEGRAM_ID
		send = f'http://api.telegram.org/bot{token}/sendMessage?chat_id={chatID}&parse_mode=Markdown&text={mensagem}'
		return requests.get(send)


def timestamp_converter():
	hora = datetime.now()
	tm = tz.gettz('America/Recife')
	hora_atual = hora.astimezone(tm)
	return hora_atual.strftime('%H:%M:%S')

def timeFrame(timeframe):

	if timeframe == 'M1':
		return 1

	elif timeframe == 'M5':
		return 5

	elif timeframe == 'M15':
		return 15

	elif timeframe == 'M30':
		return 30

	elif timeframe == 'H1':
		return 60
	else:
		return 'erro'


def verificarStop(lucroTotal):
	if lucroTotal >= abs(float(config['stop_win'])):
		deustop = 'WIN'
	elif lucroTotal <= (abs(float(config['stop_loss'])) * -1.0):
		deustop = 'LOSS'
	else:
		deustop = False
	if deustop:
		Mensagem(f' STOP {deustop} BATIDO!!! - Resultado: {float(round(lucroTotal, 2))}', True)
		sys.exit()


def buscarMenor():
	global em_espera
	arquivo = open('./lista.csv')
	leitor = csv.reader(arquivo, delimiter=';')
	timeNow = timestamp_converter()
	f = '%H:%M:%S'
	em_espera = []
	for row in leitor:
		horario = row[2] + ":00"
		dif = int((datetime.strptime(timeNow, f) - datetime.strptime(horario, f)).total_seconds() / 60)
		# Filtro para excluir os sinais que ja se passaram os horarios
		if dif < 0:
			# Adiciona a diferença de tempo em minutos para posterior sorteio de menor valor
			row.append(dif)
			# Coloca os dados da paridade juntamente com o tempo restante para entrada em uma lista
			em_espera.append(row)

	# Verifica se a lista tem sinais pendentes para operar, caso contrario retorna false para encerrar o bot
	if len(em_espera) == 0:
		em_espera = False
		Mensagem(f'Lista de sinais finalizada..\nLucro: R${str(round(lucroTotal, 2))}')
		sys.exit()
	else:
		# Ordena a lista pela entrada mais proxima
		em_espera.sort(key=lambda x: x[4], reverse=True)
		# Informa quantos sinais restam para serem executados
		Mensagem(f'SINAIS PENDENTES: {len(em_espera)}')
		# Informa o próximo sinal a ser executado
		Mensagem(f'PROXIMO: {em_espera[0][1]} | TEMPO: {em_espera[0][0]} | HORA: {em_espera[0][2]} | DIREÇÃO: {em_espera[0][3]}')


def noticas(paridade):
	global noticas

	if noticias == 'S':
		try:
			objeto = json.loads(texto)

			# Verifica se o status code é 200 de sucesso
			if response.status_code != 200 or objeto['success'] != True:
				print('Erro ao contatar notícias')

			# Pega a data atual
			data = datetime.now()
			tm = tz.gettz('America/Sao Paulo')
			data_atual = data.astimezone(tm)
			data_atual = data_atual.strftime('%Y-%m-%d')
			tempoAtual = data.astimezone(tm)
			minutos_lista = tempoAtual.strftime('%H:%M:%S')

			# Varre todos o result do JSON
			for noticia in objeto['result']:
				# Separa a paridade em duas Ex: AUDUSD separa AUD e USD para comparar os dois
				paridade1 = paridade[0:3]
				paridade2 = paridade[3:6]

				# Pega a paridade, impacto e separa a data da hora da API
				moeda = noticia['economy']
				impacto = noticia['impact']
				atual = noticia['data']
				data = atual.split(' ')[0]
				hora = atual.split(' ')[1]

				# Verifica se a paridade existe da noticia e se está na data atual
				if moeda == paridade1 or moeda == paridade2 and data == data_atual:
					formato = '%H:%M:%S'
					d1 = datetime.strptime(hora, formato)
					d2 = datetime.strptime(minutos_lista, formato)
					dif = (d1 - d2).total_seconds()
					# Verifica a diferença entre a hora da noticia e a hora da operação
					minutesDiff = dif / 60

					# Verifica se a noticia irá acontencer 30 min antes ou depois da operação
					if minutesDiff >= -30 and minutesDiff <= 0 or minutesDiff <= 30 and minutesDiff >= 0:
						if impacto > 1:
							return impacto, moeda, hora, True
					else:
						pass
				else:
					pass
			return 0, 0, 0, False
		except:
			print('Erro ao verificar notícias!! Filtro não funcionará')
			return 0, 0, 0, False
	else:
		return 0, 0, 0, False


def Payout(par, timeframe):
	API.subscribe_strike_list(par, timeframe)
	while True:
		d = API.get_digital_current_profit(par, timeframe)
		if d > 0:
			break
		time.sleep(1)
	API.unsubscribe_strike_list(par, timeframe)
	return float(d / 100)


def checkProfit(par, timeframe):
	all_asset = API.get_all_open_time()
	profit = API.get_all_profit()

	digital = False
	binaria = False

	if timeframe == 60:
		return 'binaria'

	if all_asset['digital'][par]['open']:
		digital = Payout(par, timeframe)
		digital = round(digital, 2)

	if all_asset['turbo'][par]['open']:
		binaria = round(profit[par]["turbo"], 2)

	if digital or binaria:
		if binaria < digital:
			return "digital"

		elif digital < binaria:
			return "binaria"

		elif digital == binaria:
			return "digital"
	else:
		return False


def entradas(status, id, par, dir, timeframe, opcao, n, valorGaleSinal):
	global galeRepete, lucroTotal, parAntigo, direcaoAntigo, timeframeAntigo, valor_entrada, proxSinal, valorGaleProxSinal

	if opcao == 'digital':
		while True:
			resultado, lucro = API.check_win_digital_v2(id)

			if resultado:
				lucroTotal += lucro

				if lucro > 0:
					n = 1
					valorGaleSinal = config['entrada']
					valor_entrada = float(config['entrada'])
					Mensagem(f'{id} | {par} -> win | R${str(round(lucro, 2))}\n Lucro: R${str(round(lucroTotal, 2))}\n')
					buscarMenor()
					pass
				elif lucro == 0.0:
					n = 1
					valorGaleSinal = config['entrada']
					valor_entrada = float(config['entrada'])
					Mensagem(f'{id} | {par} -> dogi | R$0\n Lucro: R${str(round(lucroTotal, 2))}\n')
					buscarMenor()
					pass
				else:
					Mensagem(f'{id} | {par} -> loss | R${str(round(lucro, 2))}\n Lucro: R${str(round(lucroTotal, 2))}\n')
					if galeVela == 'S':
						parAntigo = par
						direcaoAntigo = dir
						timeframeAntigo = timeframe
						valorGaleSinal = round(float(valorGaleSinal) * float(config['valorGale']), 2)
						if valorGaleSinal < (round(float(config['entrada']) * int(config['niveis']) * float(config['valorGale']), 2) + 0.01):
							galeRepete = True
							valorGaleProxSinal = valorGaleSinal
							pass
						else:
							valorGaleProxSinal = config['entrada']
							galeRepete = False
							buscarMenor()
							pass

					elif galeSinal == 'S':
						valorGaleSinal = round(float(valorGaleSinal) * float(config['valorGale']), 2)
						if n <= int(config['niveis']):
							Mensagem(f' MARTINGALE NIVEL {n} NO PAR {par}..')
							status, id = API.buy_digital_spot(par, valorGaleSinal, dir, timeframe)
							n += 1
							Thread(target=entradas, args=(status, id, par, dir, timeframe, opcao, n, valorGaleSinal), daemon=True).start()
							pass
						else:
							n = 1
							valorGaleSinal = config['entrada']
							buscarMenor()
							pass
					pass
				verificarStop(lucroTotal)
				break

	elif opcao == 'binaria':
		if status:
			resultado, lucro = API.check_win_v4(id)

			if resultado:
				lucroTotal += lucro

				if resultado == 'win':
					n = 1
					valorGaleSinal = config['entrada']
					valor_entrada = float(config['entrada'])
					Mensagem(f'{id} | {par} -> win | R${str(round(lucro, 2))}\n Lucro: R${str(round(lucroTotal, 2))}\n')
					buscarMenor()
					pass
				elif resultado == 'equal':
					n = 1
					valorGaleSinal = config['entrada']
					valor_entrada = float(config['entrada'])
					Mensagem(f'{id} | {par} -> doji | R$0\n Lucro: R${str(round(lucroTotal, 2))}\n')
					buscarMenor()
					pass
				elif resultado == 'loose':
					Mensagem(f'{id} | {par} -> loss | R${str(round(lucro, 2))}\n Lucro: R${str(round(lucroTotal, 2))}\n')
					if galeVela == 'S':
						parAntigo = par
						direcaoAntigo = dir
						timeframeAntigo = timeframe
						valorGaleSinal = round(float(valorGaleSinal) * float(config['valorGale']), 2)
						if valorGaleSinal < (round(float(config['entrada']) * int(config['niveis']) * float(config['valorGale']), 2) + 0.01):
							galeRepete = True
							pass
						else:
							valorGaleSinal = float(config['entrada'])
							galeRepete = False
							buscarMenor()
							pass

					elif galeSinal == 'S':
						valorGaleSinal = round(float(valorGaleSinal) * float(config['valorGale']), 2)
						if n <= int(config['niveis']):
							Mensagem(f' MARTINGALE NIVEL {n} NO PAR {par}..')
							status, id = API.buy(valorGaleSinal, par, dir, timeframe)
							n += 1
							Thread(target=entradas, args=(status, id, par, dir, timeframe, opcao, n, valorGaleSinal), daemon=True).start()
							pass
						else:
							n = 1
							valorGaleSinal = config['entrada']
							buscarMenor()
							pass
					pass
				verificarStop(lucroTotal)

		else:
			Mensagem('Error')


def tendenciaEHit(par, timeframe, direcao):
	if analisarTendencia == 'S' and hitdeVela == 'N':
		velas = API.get_candles(par, (int(timeframe) * 60), 20, time.time())
		ultimo = round(velas[0]['close'], 4)
		primeiro = round(velas[-1]['close'], 4)
		diferenca = abs(round(((ultimo - primeiro) / primeiro) * 100, 3))
		tendencia = "call" if ultimo < primeiro and diferenca > 0.01 else "put" if ultimo > primeiro and diferenca > 0.01 else direcao
		return tendencia, False
	elif analisarTendencia == 'N' and hitdeVela == 'S':
		velas = API.get_candles(par, (int(timeframe) * 60), 5, time.time())
		velas[0] = 'r' if velas[0]['open'] > velas[0]['close'] else 'g'
		velas[1] = 'r' if velas[1]['open'] > velas[1]['close'] else 'g'
		velas[2] = 'r' if velas[2]['open'] > velas[2]['close'] else 'g'
		velas[3] = 'r' if velas[3]['open'] > velas[3]['close'] else 'g'
		hit = velas[0] + velas[1] + velas[2] + velas[3]
		if hit == 'rrrr' or hit == 'gggg':
			return direcao, True
		else:
			return direcao, False
	elif analisarTendencia == 'S' and hitdeVela == 'S':
		velas = API.get_candles(par, (int(timeframe) * 60), 20, time.time())
		ultimo = round(velas[0]['close'], 4)
		primeiro = round(velas[-1]['close'], 4)
		diferenca = abs(round(((ultimo - primeiro) / primeiro) * 100, 3))
		tendencia = "call" if ultimo < primeiro and diferenca > 0.01 else "put" if ultimo > primeiro and diferenca > 0.01 else direcao

		velas[15] = 'r' if velas[15]['open'] > velas[15]['close'] else 'g'
		velas[16] = 'r' if velas[16]['open'] > velas[16]['close'] else 'g'
		velas[17] = 'r' if velas[17]['open'] > velas[17]['close'] else 'g'
		velas[18] = 'r' if velas[18]['open'] > velas[18]['close'] else 'g'
		hit = velas[15] + velas[16] + velas[17] + velas[18]
		if hit == 'rrrr' or hit == 'gggg':
			return tendencia, True
		else:
			return tendencia, False
	else:
		return direcao, False


def operar(valor_entrada, par, direcao, timeframe, horario, opcao):
	status = False
	try:
		if opcao == 'digital':
			status, id = API.buy_digital_spot(par, valor_entrada, direcao, timeframe)
			Thread(target=entradas, args=(status, id, par, direcao, timeframe, opcao, 1, valor_entrada), daemon=True).start()
		elif opcao == 'binaria':
			status, id = API.buy(valor_entrada, par, direcao, timeframe)
			Thread(target=entradas, args=(status, id, par, direcao, timeframe, opcao, 1, valor_entrada), daemon=True).start()
		else:
			Mensagem('ERRO AO REALIZAR ENTRADA!!')
			time.sleep(1)
	except:
		Mensagem('ERRO AO REALIZAR ENTRADA!!')
		time.sleep(1)

	if status:
		Mensagem(f'\n INICIANDO OPERAÇÃO {str(id)}..\n {str(horario)} | {par} | OPÇÃO: {opcao.upper()} | DIREÇÃO: {direcao.upper()} | M{timeframe}\n\n')
		buscarMenor()


API.connect()
API.change_balance(config['conta'])
while True:
	if API.check_connect() == False:
		print('>> Erro ao se conectar!\n')
		input('   Aperte enter para sair')
		sys.exit()
	else:
		Clear_Screen()
		print('>> Conectado com sucesso!\n')
		print('Verificando os sinais..')
		if noticias == 'S':
			try:
				response = requests.get("http://botpro.com.br/calendario-economico/")
				texto = response.content
			except:
				print('Erro ao carregar json de notícias!!')
		config['banca_inicial'] = banca()
		break
print('Pressione Ctrl+C para sair\n')

try:
	buscarMenor()
	while True:
		timeNow = timestamp_converter()
		print(datetime.now().strftime('%d/%m/%Y %H:%M:%S'), end='\r')

		for row in em_espera:
			horario = row[2]
			if galeRepete:
				par = parAntigo
				direcao = direcaoAntigo
				timeframe = timeframeAntigo
				valor_entrada = valorGaleProxSinal
			else:
				par = row[1].upper()
				direcao = row[3].lower()
				timeframe_retorno = timeFrame(row[0])
				timeframe = 0 if (timeframe_retorno == 'error') else timeframe_retorno
				valor_entrada = config['entrada']

			s = horario + ":00"
			f = '%H:%M:%S'
			dif = (datetime.strptime(timeNow, f) - datetime.strptime(s, f)).total_seconds()

			if dif == -50:
				opcao = checkProfit(par, timeframe)
				if not opcao:
					Mensagem(f' PARIDADE FECHADA! ABORTANDO ENTRADA!!')
					time.sleep(1)
					buscarMenor()

			if dif == -10:
				tend, hit = tendenciaEHit(par, timeframe, direcao)

			if dif == -2:
				impacto, moeda, hora, stts = noticas(par)
				if stts:
					Mensagem(f' NOTÍCIA COM IMPACTO DE {impacto} TOUROS NA MOEDA {moeda} ÀS {hora}!')
					time.sleep(1)
					buscarMenor()
					pass
				else:
					if tend != direcao:
						Mensagem(f' PARIDADE {par} CONTRA TENDÊNCIA!\n')
						time.sleep(1)
						buscarMenor()
						pass
					else:
						if hit:
							Mensagem(f' HIT DE VELA NA PARIDADE {par}!\n')
							time.sleep(1)
							buscarMenor()
							pass
						else:
							operar(valor_entrada, par, direcao, timeframe, horario, opcao)

		time.sleep(1)
except KeyboardInterrupt:
	exit()
