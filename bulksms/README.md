# BulkSMS 1.0

Aplicativo profissional de linha de comando para Android com Termux + Termux:API. Use apenas com contatos que autorizaram receber SMS.

## Instalação

```bash
cd bulksms
chmod +x install.sh start.sh
./install.sh
```

O instalador atualiza pacotes e instala Python, `termux-api`, `requests`, `rich`, `typer`, `pandas` e `openpyxl`.

## Permissões do Termux e Termux:API

1. Instale o aplicativo **Termux:API** no Android.
2. No Termux, execute `pkg install termux-api` se ainda não instalou.
3. Conceda permissão de SMS ao Termux/Termux:API nas configurações do Android.
4. Teste com: `termux-sms-send -n +258841234567 "teste autorizado"`.

## Como importar arquivos

Coloque arquivos em `contacts/` nos formatos:

- `.csv`
- `.txt`
- `.xlsx`

O sistema elimina linhas vazias, remove duplicados e normaliza números de Moçambique para `+258` quando o usuário informar números nacionais como `841234567`.

## Mensagens

Coloque mensagens em `messages/` como arquivos `.txt` ou escolha a opção de digitar a mensagem no teclado.

## Como iniciar

```bash
cd bulksms
./start.sh
```

Menu principal:

1. Importar contatos
2. Listar arquivos
3. Escolher mensagem
4. Iniciar envio
5. Estatísticas
6. Ver logs
7. Configurações
8. Ajuda
9. Sair

## Atualizar do GitHub

Quando adicionar novos contatos no GitHub, atualize a pasta local com:

```bash
git pull --ff-only
```

Também é possível executar a atualização pelo menu **Configurações**. O comando fica em `config.json` como `github_update_command`.

## Gerar contatos de Moçambique +258

No menu **Configurações**, escolha gerar contatos. Informe a quantidade desejada e o sistema criará um arquivo `contacts/mozambique_QUANTIDADE.txt` com números `+258` sequenciais para testes autorizados.

## Logs

Cada envio cria um CSV em `logs/` com data, hora, número, status, mensagem e erro quando existir. Use o menu **Ver logs** para visualizar os registros recentes.

## Observações legais

Envie mensagens apenas para contatos autorizados. O BulkSMS continua após falhas, aguarda 1 segundo entre envios e registra sucesso ou erro de cada número.
