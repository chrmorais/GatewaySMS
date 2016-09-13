# Gateway SMS

Este software toma conta do envio, confirmação e recebimento de mensagens SMS. Trabalha da forma mais autônoma possível, minimizando a necessidade de manutenção.

O software foi concebido para trabalhar com diversos provedores de SMS ao mesmo tempo (por exemplo Zenvia, MobiPronto, ou mesmo
diretamente com as operadoras de telefonia). No momento há apenas um provedor implementado (Zenvia).

Entre em contato (epxx@epxx.co) se precisar de ajuda.

# Checklist de implementação

Como a única interface implementada é para Zenvia, o checklist presume que você vá utilizar esse provedor, mas a seqüência
seria parecida para qualquer outro provedor, desde que a interface já esteja implementada e testada.

Para colocar o servidor no ar, a lista básica de tarefas é a seguinte:

1) Instalar este software num servidor.

O ideal é rodar o servidor num container próprio, como por exemplo uma máquina na nuvem, separada da rede corporativa.
Se fizer uso de call-back (vide item 3) o servidor deve ser uma máquina com IP fixo,
nome DNS e porta 33774 aceitando conexões de fora.

2) Obter uma conta com a Zenvia. (O provedor oferece contas de teste com 10 créditos.)

3) Configurar corretamente a sua conta junto ao Zenvia.

Este software faz uso da API HTTP do Zenvia. (O provedor oferece outras opções, como envio de arquivos via Web e REST.)

As confirmações de entrega podem ser recebidas por consulta periódica ou por
call-back. Se você quer receber mensagens SMS dos clientes, é obrigatório usar call-back. No modo call-back,
o servidor da Zenvia abre uma conexão com o servidor, por isso é necessário ter IP fixo, nome DNS e
porta 33774 liberada nesse modo.

Se você usar call-back, é preciso contactar a Zenvia para configurar as URLs de call-back para a sua conta,
que seriam algo como http://sms.seudominio.com:33774/statussms (para receber as confirmações de
entrega) e http://sms.seudominio.com:33774/recebsms (para receber mensagens de clientes).
Substitua o domínio sms.seudominio.com pelo nome DNS do seu servidor ou mesmo pelo IP fixo.

4) Configurar o servidor

A configuração é feita diretamente no início nos arquivos sms.py e servidor.py, que também são os executáveis.  O segundo
executável implementa o servidor HTTP que atente as requisições de call-back, e só é preciso
configurar se você fizer uso de call-back.

Nesses arquivos você preencherá o usuário e senha Zenvia, bem como o e-mail de administrador para
receber avisos, etc.

5) Testar o servidor

Para testar o envio de mensagens, crie um lote de teste (continue lendo a documentação para conhecer o formato!),
jogue na pasta INBOX e execute o programa sms.py.

Se tudo correr bem, a mensagem será entregue. Se não, consulte o log na pasta LOG para ver o que aconteceu.

Se você optou por usar call-back, rode o executável servidor.py, e envie um lote de teste para um celular que 
você possa usar. A confirmação deve ser entregue por conexão entrante, o que pode ser verificado no log.

Você também deve testar a recepção de mensagens do cliente, enviando um SMS de resposta a partir do celular
que recebeu a mensagem do lote.

(A princípio, só é possível receber SMS de "resposta", onde seu cliente responde a um SMS que você enviou.
É possível receber mensagens sem ser de resposta, como por exemplo uma consulta automatizada, mas nesse
caso é preciso contratar um número exclusivo para sua empresa junto à Zenvia, e os clientes poderão então
enviar consultas a esse número.)

6) Colocar o servidor em produção

A interface com o sistema ERP é extremamente simples, consistindo na troca de arquivos através de duas pastas: INBOX e OUTBOX.
O ERP posta arquivos CSV com mensagens a enviar na pasta INBOX, e retira arquivos CSV com as confirmações bem como mensagens
recebidas. 

O gateway move os arquivos da pasta INBOX para outras pastas conforme o envio é processado, até o destino final (pasta LIXO).
O arquivo original não é modificado em nenhuma fase.

Você deve definir rotinas ou scripts que vão copiar arquivos para dentro do INBOX, e retirar as respostas
de OUTBOX, de modo a estabelecer a comunicação por lote com seu sistema corporativo.

O executável sms.py deve ser programado para rodar periodicamente, e.g. a cada 15 minutos, usando crontab
ou técnica similar.

O executável servidor.py deve ser executado quando o servidor for ligado, se você optou por usar call-back.
A execução deve ser monitorada, ou seja, se o executável sair por qualquer motivo, deve ser rodado novamente.
Isso também pode ser feito usando-se crontab e scripts.

Certifique-se que o servidor consegue enviar e-mails para fora, de modo que os e-mails de aviso do 
SMS cheguem ao destino. Instale o pacote "mailx" e faça uso do utilitário mail, usando o mesmo usuário
que roda o servidor SMS, para fazer essa checagem.

Considere fazer uso de um serviço como New Relic para monitorar a URL http://sms.seudominio.com:33774/ping.html
e garantir que o servidor de call-back esteja mesmo rodando e esteja acessível.

Verifique periodicamente o log do servidor para detectar problemas. Se você manda lotes grandes com
grande freqüência, considere adicionar um celular de "canário" que sempre recebe mensagens, e escale
alguém para verificar que o SMS está chegando.

# Formato e interface INBOX

Formato CSV, uma linha por mensagem, campos separados por ponto-e-vírgula e sem aspas. 

ID;charset;telefone;dd/mm/aaaa hh:mm:ss;mensagem

ID é um identificador único para cada mensagem. Pode ser de qualquer natureza (contador, hash, etc.) mas deve identificar unicamente a mensagem por um tempo razoável. O tamanho é livre mas o ideal é usar 16 caracteres ou menos. 

Idealmente, o ID deve ser único para sempre, para permitir rastreio de cada mensagem dentro dos logs. Se várias mensagens com o mesmo ID entrarem no sistema durante a janela de confirmação (48h), apenas uma versão será mandada e confirmada.

O charset é a forma que os caracteres acentuados são codificados na mensagem. Se a mensagem não tem acentos, utilize ascii. De maneira geral as mensagens SMS não devem ser acentuadas, nem utilizar caracteres especiais. Veja a seção “Formato das mensagens SMS” para mais detalhes.

O telefone é simplesmente o telefone celular que deve receber a mensagem SMS. Desde que o telefone seja válido, ele pode estar em qualquer formato, com ou sem caracteres especiais. O gateway usa apenas os dígitos que encontrar, e adiciona automaticamente DDD e DDI de acordo com o número de dígitos. (O arquivo-fonte sms.py contém o DDD e DDI padrões para envio de mensagens.)

A hora dd/mm/aaaa hh:mm:ss é a hora em que a mensagem SMS deve ser enviada. Se a mensagem pode ser enviada imediatamente, este campo deve ser vazio. 

A mensagem é, naturalmente, a mensagem a ser enviada. Ela deve atender aos seguintes requisitos:

1) Ser compatível com o charset indicado (provavelmente será “ascii”).

2) Obedecer ao limite de 140 caracteres, e esse limite inclui o valor “origem” configurado em sms.py.

3) Mensagens acentuadas têm limite de 70 caracteres.

4) Devido ao formato do arquivo CSV, a mensagem não pode ter ponto-e-vírgula nem quebra de linha.

Leve em conta a seção “Formato das mensagens SMS” ao compor a mensagem. Diversos caracteres especiais são problemáticos por um motivo ou por outro.

Os arquivos devem ser postados com extensão .csv na pasta INBOX. Outras extensões são ignoradas.

Procure gerar um nome único para cada remessa, por exemplo ano-mes-dia.csv. O gateway lida corretamente com arquivos homônimos (adicionando sufixo .1, .2, etc.) mas o rastreio fica mais fácil com nomes mais claros, e isto diminui o risco do próprio sistema ERP sobrescrever um arquivo anterior em INBOX antes do gateway aceitá-lo.

O sistema ERP deve postar arquivos “instantaneamente” na pasta INBOX, para evitar o risco do gateway SMS ler o arquivo pela metade. (O gateway tem proteção contra esta situação mas ela não é 100% segura.) Uma sugestão é copiar o arquivo com uma extensão diferente de .csv, e renomear para .csv ao final da cópia.

# Formato das mensagens SMS

Em princípio, as mensagens SMS têm tamanho limitado a 160 caracteres. Devido a limitações de algumas tecnologias específicas (e.g. Nextel) o limite prático é de 140 caracteres. (O Twitter adotou este mesmo limite pois foi inicialmente concebido para funcionar via SMS.)

As mensagens SMS usam o conjunto de caracteres GSM, que é parecido porém diferente do padrão ASCII. Muitos sistemas não levam em conta esta diferença, então é preciso ater-se aos caracteres que têm os mesmos códigos em GSM e ASCII.

Além disso, tanto os provedores SMS quanto as operadoras de telefonia atribuem significados especiais a determinados caracteres, o que impede seu uso nas mensagens. Por exemplo, o Zenvia interpreta % e ; como delimitador, e as operadoras bloqueiam mensagens com # e @. Nosso formato de arquivo CSV também faz uso de ; para delimitar campos.

Os caracteres especiais “seguros” são os usuais de pontuação: , . : ? ! < > ( ) /

Uma alternativa emergente é codificar as mensagens no formato UCS-2 (2 bytes por caractere). Desta forma, todos os caracteres acentuados e especiais do Unicode podem ser mandados via SMS.

O UCS-2 é o futuro mas ainda tem alguns problemas:

1) Limita o tamanho máximo da mensagem em 70 caracteres;

2) Alguns celulares não mostram mensagens UCS-2 corretamente. Uma mensagem enviada do Android pode aparecer truncada no iPhone e vice-versa.

3) Nem todo provedor SMS aceita mensagens neste formato, no momento.

O provedor Zenvia alega aceitar mensagens em UTF-8, mas uma mensagem acentuada chega incorreta no telefone, até a última vez que testamos.

Além disso, o Zenvia converte mensagens acentuadas mandadas por um cliente para ASCII antes de entregá-la para nosso sistema. Por exemplo, “Ágora” é recebido como “Agora”. 

Por estes motivos, o ideal é mandar a mensagem sem acentuação e usando apenas os caracteres de pontuação listados mais acima. Isto assegura que os recipientes não verão mensagens truncadas ou embaralhadas. Mesmo as operadoras de telefonia mandam mensagens sem acentos pelo mesmo motivo.


# Formato e interface OUTBOX

O gateway posta arquivos na pasta OUTBOX com duas extensões possíveis: .env e .rec, com ou sem sufixo (.1, .2, etc.). Os primeiros são
confirmações de envio, os segundos são mensagens recebidas. 

Dentro de cada arquivo, o primeiro campo de cada registro também indica do que ele se trata (“Recebida” ou “Confirmacao”), então o sistema ERP pode usar uma única rotina para lidar com todos os arquivos que encontrar em OUTBOX, sem prestar atenção à extensão.

Os nomes dos arquivos referem-se à hora GMT (2 ou 3 horas adiantada em relação à hora brasileira) em que o software começou a rodar a sessão que gera o arquivo, então a possibilidade de ocorrer arquivos com sufixo .1, .2, etc. é muito baixa (mesmo para o caso do horário de verão), salvo se alguém mudar manualmente a hora da máquina.

Uma vez postado em OUTBOX, o arquivo não muda, então o sistema ERP pode tomar o tempo necessário para copiá-lo, e só então apagá-lo.

Os registros de confirmação de envio têm o seguinte formato (CSV, semelhante ao arquivo de entrada):

Confirmacao;ID;dd/mm/yyyy hh:mm:ss;status

A palavra “Confirmacao” é fixa e identifica o significado do registro. 

O ID é o familiar identificador único da mensagem, que o sistema ERP pode usar para relacionar a confirmação com a mensagem originalmente enviada.

A hora indica quando a confirmação foi obtida.

O status é um valor numérico que indica o que aconteceu com a mensagem. Exceto pelo código zero, todos os demais significam que a mensagem não foi entregue devido a um erro. 

0: Enviada

10: Mensagem vazia (detectada remotamente)

11: Mensagem vazia (detectada localmente)

20: Mensagem grande demais (detectada remotamente)

21: Mensagem grande demais (detectada localmente)

22: Mensagem inválida (caracteres acentuados/especiais?)

30: Telefone inválido (detectado remotamente)

31: Telefone inválido (detectado localmente)

40: Telefone nulo

50: Data de agendamento inválida

60: ID inválido (ou tempo de confirmação já passou e o provedor SMS não “lembra” mais do ID, então não é mais possível confirmar positivamente a entrega da mensagem.)

70: ID pertence a mensagem já enviada antes

80: Telefone internacional e plano não permite envio

90: Problema diverso/desconhecido

1010: Celular de destino está inativo

1015: Não entregue pela operadora, motivo não informado

1020: Celular não coberto pelo provedor

1030: Mensagem expirou na rede da operadora sem ser entregue

1040: Erro na rede de telefonia

1050: Mensagem rejeitada pelo provedor ou pela operadora (ela tem caracteres especiais “proibidos”?)

1060: Mensagem cancelada pelo provedor ou pela operadora

1070: Mensagem considerada inválida pelo operador (caracteres acentuados/especiais?) 

1080: Número inválido

1090: Mensagem bloqueada pela operadora

1100: Mensagem filtrada pelo provedor ou pela operadora (pode ter sido considerada “spam”)

1110: Telefone internacional não coberto pelo plano do provedor

1120: Provedor inválido (erro interno do sistema, caso um provedor seja removido enquanto houver mensagens SMS pendentes de confirmação do mesmo)

1130: Problema diverso/desconhecido

1140: ID desconhecido (ou tempo de confirmação já passou e o provedor SMS não “lembra” mais do ID, então não é mais possível confirmar positivamente a entrega da mensagem.)

1999: Mensagem expirada (o provedor não retornou nenhuma informação e presume-se que o SMS foi perdido)

Os valores abaixo de 1000 referem-se a erros que ocorrem imediatamente ao tentar enviar a mensagem para o provedor. Os valores acima de 1000 ocorrem quando o gateway consulta o provedor a respeito das confirmações.

Os registros de recebimento de mensagem seguem o seguinte formato CSV:

Recebida;ID;Provedor;dd/mm/yyyy hh:mm:ss;fone;mensagem

A string “Recebida” é fixa e indica o tipo de registro.

“ID” é um identificador único da mensagem. Se a mensagem recebida foi uma resposta a outra mensagem enviada por nós, o ID será o mesmo do envio. Isto permite interação com o cliente (por exemplo, envia uma enquete e recebe a respectiva resposta).

“Provedor” indica qual o provedor pela qual a mensagem foi recebida (e.g. “Zenvia”). Esta informação é pouco útil hoje,  mas pode ter utilidade futura (e.g. se a resposta tem de voltar através do mesmo provedor). 

A hora indica quando a mensagem foi recebida.

A “mensagem” enviada pelo cliente pode ou não conter acentos, e é sempre codificada no padrão UTF-8.

UTF-8 é a forma mais compatível de codificar Unicode, e tem a vantagem adicional de ser igual a ASCII se a mensagem não contém caracteres acentuados.

# Recebimento de mensagens

O gateway suporta a recepção de mensagens emitidas pelos clientes sob duas condições:

1) Quando o cliente responde diretamente a uma mensagem que foi enviada.

2) Quando o cliente envia a mensagem para um número exclusivo contratado junto ao provedor (esse tipo de número tem 5 ou 6 dígitos).

 A segunda opção é mais poderosa, pois permite ao cliente iniciar uma consulta ao sistema, mas depende da contratação deste serviço junto ao provedor, e custos extras.

No nível de comunicação entre este gateway e o provedor, há também duas formas de obter as mensagens recebidas, bem como obter o estado das mensagens enviadas: polling (consulta periódica) e call-back (o provedor toma a iniciativa de conectar-se ao nosso software).

Sem dúvida o call-back é mais poderoso, pois recebemos a mensagem imediatamente após envio do cliente, e a resposta também pode ser imediata. Por outro lado, o call-back implica em haver uma porta aberta no servidor para a Internet. Isto traz implicações de segurança e administração do servidor.

O provedor Zenvia só permite o recebimento de mensagens via call-back, embora permita a confirmação de envio pelos dois métodos. Assim, este gateway não precisa ficar exposto à Internet se for utilizado apenas para enviar mensagens. (Neste caso a configuração "zenvia_confirm_http" no arquivo sms.py deve ser igual a False, para que as confirmações sejam obtidas por polling.)

# Emitente das mensagens

Quando o cliente recebe uma mensagem SMS, o número de 5 ou 6 dígitos de origem é o do provedor, a não ser que se contrate um número exclusivo. (O número exclusivo também permite que o cliente inicie uma interação, conforme foi explicado no tópico anterior.)

Além do número, um nome de emitente pode ser enviado juntamente com cada mensagem. No código-fonte sms.py, o atributo “origem” contém este nome. Infelizmente ele ocupa espaço no limite de 140 caracteres da mensagem, limitando ainda mais o tamanho do texto útil.

# Funcionamento periódico

Na presente implementação, o gateway processa os lotes pendentes de envio e confirmação, e então encerra. A confirmação das mensagens enviadas, bem como uma nova tentativa de envio em caso de falha, só ocorre quando o gateway é rodado novamente.

O executável sms.py deve ser rodado periodicamente (e.g. a cada 15 minutos) para que o processo flua com agilidade razoável sem sobrecarregar o provedor. Em sistemas Unix/Linux, a forma mais simples de fazer isto é via crontab.

O software tem uma proteção contra execução de mais uma instância ao mesmo tempo (obter um recurso do computador que só pode pertencer a um processo de cada vez). Esta proteção é implementada em trava.py.

Quando o provedor fornece as mensagens recebidas e confirmadas via call-back, tais mensagens são armazenadas em arquivos temporários, e entregues na pasta OUTBOX apenas quando o executável principal é rodado.

Se o sistema ERP precisar de mais agilidade (por exemplo, para responder em tempo real a perguntas enviadas via SMS) o sistema deverá ser modificado para mandar as mensagens para OUTBOX de forma imediata, e também enviar a resposta em INBOX mais rapidamente. Estas modificações são possíveis mas não estão implementadas nesta versão do gateway.

# Pastas de arquivos

As mensagens trafegam por um número de pastas ao longo do seu processamento:

INBOX: Onde o sistema ERP posta os arquivos .csv para envio. Cada arquivo é chamado de lote no código-fonte.

INVALIDO: Lotes com problemas de parsing (CSV inválido) são movidos para cá. Neste caso, nenhuma mensagem do lote é enviada.

ENVIAR: Lotes “bons” são movidos para esta pasta e processados para envio.
O lote só sai desta pasta para o LIXO quando todas as mensagens do mesmo foram enviadas.

ENVIADAS: As mensagens já enviadas de um lote são gravadas nesta pasta. Para cada lote é criado um arquivo .csv.env.
Quando todas as mensagens do lote foram enviadas, o .csv.env também é movido para o LIXO.

CONFIRMAR: As mensagens enviadas com sucesso mas pendentes de confirmação são anotadas em arquivos ano-mes-dia.conf. 
Mensagens devidamente confirmadas são anotadas em arquivos ano-mes-dia.recibo.

Quando os respectivos arquivos .conf e .recibo têm o mesmo número de mensagens, ambos são movidos para o LIXO.

Confirmações recebidas via call-back são gravadas em diversos arquivos provisórios de nome prefixo-d.recibo, que são convertidos para ano-mes-dia.recibo no ciclo normal de processamento.

LIXO: Destino final dos lotes e arquivos auxiliares quando o processamento foi 100% completado.

RECEPCAO: Rascunho para arquivos .env (gravados quando uma confirmação positiva ou erro fatal é obtido) e .rec (gravados quando uma mensagem é recebida). Mensagens recebidas por call-back também são gravadas nesta pasta, a diferença é que os arquivos têm a forma -d.rec.

Ao final do ciclo de processamento, os arquivos nesta pasta são movidos para OUTBOX.

OUTBOX: Arquivos de confirmação e recepção de mensagens, no formato ano-mes-dia-hora-minuto-segundo, com extensão .rec ou .env.

Também há pastas auxiliares do funcionamento do gateway:

STAT: O sistema grava a hora de início de funcionamento para medir o tempo de cada sessão. (Sessões de mais de 2h indicam um processo travado e o administrador deve ser avisado.)

LOG:  Log do sistema, gravado no formato log-ano-mes-dia.log. Falhas no software também são registradas no log.

# Segurança ao lidar com os dados

O gateway foi concebido de forma a evitar ao máximo perdas de dados, além de ser fácil de instalar e manter funcionando.  O que levou a algumas decisões de design.

O sistema utiliza arquivos simples (linhas de texto) em vez de um banco de dados, pois sua integridade é mais fácil de garantir. (Cada banco de dados tem uma semântica diferente no que se refere à integridade.)

Usar arquivos também evita uma dependência: um banco de dados teria de ser instalado, configurado, etc.

Os arquivos de dados nunca são modificados. Eles são apenas movidos, ou são acrescentadas dados a eles.

Quando um arquivo é movido, sempre é verificado se existe um arquivo homônimo na pasta de destino. Se sim, o novo arquivo movido recebe um sufixo.

Todo acréscimo de dados a qualquer arquivo (seja de dados ou log) é sincronizado, linha a linha. Se o processo for interrompido por qualquer motivo, perde-se no máximo uma linha de registro (e.g. uma mensagem enviada).

Os “lotes” – arquivos CSV postados na pasta INBOX – são sempre manipulados inteiros. Primeiramente eles são movidos para ENVIAR, e dali para o LIXO.

Quando um lote foi parcialmente enviado, as mensagens ainda não enviadas são identificadas comparando-se o lote em ENVIAR com o respectivo registro de envio na pasta ENVIADAS.

# Testes de confiabilidade

O servidor de call-back que roda na porta 33774 serve uma página /ping.html apenas para fins de teste. O conteúdo da resposta contém o número 42, entre outros dados aleatórios. O acesso periódico a esta página é uma forma de verificar que o servidor está rodando corretamente. Sugere-se utilizar um serviço externo como New Relic para este fim.

Se o servidor de call-back está funcionando, muito provavelmente a recepção de mensagens também estará ok, embora seja importante que outros testes positivos continuem sendo feitos (como usar “canários” ou usuários-cobaia ao fazer campanhas de remessa SMS a clientes, principalmente se o SMS pede resposta do cliente).

Para testar o envio de mensagens de forma periódica e automática, sugerimos que um script invocado periodicamente pelo crontab poste uma mensagem no INBOX.

# Descrição do código-fonte

O código-fonte segue uma abordagem procedural. A orientação a objetos não foi utilizada pois cada módulo já funciona como um objeto singleton.

# Executável sms.py (processamento do lote)

Executável do processamento de lote, que deve ser rodado periodicamente (e.g. a cada uma hora).

Os defaults do software (conta, senha, e-mail do administrador, etc.) estão configurados neste arquivo.

# Executável servidor.py (servidor de call-back)

Servidor que atende a porta HTTP 33774 e recebe as chamadas de call-back do provedor de SMS. Este executável roda sem nunca sair, a não ser em caso de erro.

No momento apenas a API de call-back compatível com Zenvia é implementada, mas este módulo pode atender e distribuir conexões de diversos provedores conforme necessário.

Se o acordo com o provedor SMS é receber confirmações e/ou mensagens do cliente via call-back, este serviço precisa ficar rodando o tempo todo num servidor acessível a partir da Internet.

 Se as confirmações são recebidas via call-back, a configuração 'zenvia_confirm_http' no arquivo sms.py deve ser igual a True. Se as confirmações são obtidas por requisição periódica, esta configuração deve ser igual a False.

Sua conta no provedor de SMS, por exemplo Zenvia, tem de ser corretamente configurada para que o provedor saiba qual é o endereço e porta
do seu servidor. Idealmente a máquina em que este servidor roda deve ter IP fixo e um nome DNS, para que a URL fornecida ao provedor
seja algo como http://sms.meudominio.com:33774/recebsms e http://sms.meudominio.com:33774/statussms.

# telefone.py

Este módulo consiste números de telefone, verificando se parecem válidos, adicionando DDD e DDI se aparentam não ter esta informação, de acordo com o comprimento. (Todo número de celular deve ser completo com DDD e DDI para entrega de SMS.)

Também pode decidir que provedor será utilizado para enviar uma mensagem para determinado número. No momento todos os números são direcionados para o provedor padrão configurado em sms.py.

No presente momento este módulo não verifica positivamente os números junto a um cadastro remoto, nem conhece o Plano de Numeração do Brasil ou de outros países, de modo que sua capacidade de detectar números inválidos é limitada.

(De qualquer forma, números inválidos serão rejeitados pelo provedor, então o relatório de entrega em OUTBOX listará as mensagens com estes números, com erro 30 ou 1080. A questão é detectar os erros antes mesmo de tentar enviar.)

O módulo não lida corretamente com números internacionais, pois em alguns países a combinação DDI + DDD + celular pode ter o mesmo tamanho que a combinação brasileira DDD + telefone de 9 dígitos.

Exemplo: telefone americano +1 989 555 2345, telefone brasileiro (19) 89555-2345. Olhando exclusivamente para os dígitos, não é possível distinguir um do outro, a não ser que se conheça o plano de numeração dos dois países em profundidade (no caso, todo telefone celular brasileiro com nove dígitos começa com “9”, então podemos inferir que o número não é brasileiro).

A implementação de entrega via diferentes provedores conforme a operadora não está implementada, embora esteja prevista no código. Este tipo de escolha envolve comunicação com algum serviço remoto, já que a portabilidade não permite mais determinar a operadora em função do Plano de Numeração.

# zenvia.py

Implementação da comunicação com o provedor Zenvia. Os códigos de erro específicos do Zenvia são traduzidos para os códigos adotados neste software.

