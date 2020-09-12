# bot-sinais-2.0
Bot para operar na IQ Option seguindo uma lista de sinais com threads

# Configurações
1. Abra o config.txt e utilize S ou N para as funções desejadas
2. Abra o lista.csv como bloco de notas e adicione os sinais a partir da segunda linha (Não deixe nenhuma linha em branco no final).
3. Execute o main.py com o python, digite email e senha da IQ e seja feliz.
<p></p>
 Formato aceito:
  <p></p>
TEMPO;PAR;HORA;DIRECAO<p></p>
M5;EURJPY;11:05;PUT;

# Funções
- Stop wins e loss.
- MartinGale próxima vela.
- MartinGale próximo sinal.
- Analisador de tendência (não opera contra tendência).
- Analisador de notícias (não opera com notícias de 2 ou 3 touros na moeda).
- Hit de vela (não opera se houver hit de vela no gráfico).
- Bot telegram.

**_Caso precise de um catalogador de traders, acesse:_**
[IQ Top Traders](http://iqtoptraders.ga/)
