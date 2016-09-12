# -*- coding: utf-8

# Tipos de status permitidos para enviadas.registrar(). Mensagens que apresentarem
# estes erros no envio são consideradas "enviadas" e são listadas em OUTBOX, pois
# são erros fatais e não adianta tentar novamente. O sistema ERP deverá lidar com
# os erros.

STATUS_ENVIADO = 0
STATUS_MSGNULA = 10
STATUS_MSGNULA_LOCAL = 11  # erro reportado por nós, não pelo gateway
STATUS_MSGGRANDE = 20
STATUS_MSGGRANDE_LOCAL = 21 # idem
STATUS_MSGINVAL = 22
STATUS_FONEINVAL = 30
STATUS_FONEINVAL_LOCAL = 31 # idem
STATUS_FONENULO = 40
STATUS_DATAINVAL = 50
STATUS_IDINVAL = 60
STATUS_IDENVIADO = 70
STATUS_INTERNACIONAL = 80
STATUS_OUTRO = 90

# Tipos de status permitidos para confirmacao.registrar(). Estes status
# são reportados depois que a mensagem tinha sido aceita para envio pelo
# provedor. Os códigos são diferentes dos STATUS_* pois as mensagens com
# erro STATUS_* são reportadas diretamente na pasta OUTBOX.

CONFIRM_ENTREGUE = 0
CONFIRM_INATIVO = 1010
CONFIRM_SEMINFORMACAO = 1015
CONFIRM_NAOCOBERTO = 1020
CONFIRM_EXPIRADA = 1030
CONFIRM_ERROREDE = 1040
CONFIRM_REJEITADA = 1050
CONFIRM_CANCELADA = 1060
CONFIRM_MSGINVAL = 1070
CONFIRM_NUMEROINVAL = 1080
CONFIRM_BLOQUEADA = 1090
CONFIRM_SPAM = 1100
CONFIRM_INTERNACIONAL = 1110
CONFIRM_GATEWAYINVAL = 1120
CONFIRM_OUTRO = 1130
CONFIRM_IDDESCONHECIDO = 1140

# Erro especial pois a mensagem foi enviada mas nunca houve resposta
# do provedor, ou a resposta se perdeu devido a alguma falha

CONFIRM_TIMEOUT = 1999
