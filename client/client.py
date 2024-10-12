import websocket
import threading
from datetime import datetime
import sys
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Obtém a chave de criptografia do arquivo .env
KEY = os.getenv('KEY')

# Verifica se a chave de criptografia foi carregada corretamente
if not KEY:
    raise ValueError("Chave de criptografia não definida no arquivo .env")

# Inicializa o conjunto de cifras (cipher suite) com a chave carregada
cipher_suite = Fernet(KEY.encode())  # Certifique-se de codificar para bytes

# Configuração do servidor WebSocket
SERVER_IP = "localhost"  # Altere para o IP do servidor se necessário
SERVER_PORT = 8765        # Altere para a porta do servidor se necessário
websocket_url = f"ws://{SERVER_IP}:{SERVER_PORT}"

# Dicionário de usuários e senhas
usuarios = {
    "bob": "senha_bob",
    "alice": "senha_alice"
}

def login():
    """
    Função de login que solicita o nome de usuário e senha.
    Retorna o nome do usuário após um login bem-sucedido.
    """
    while True:
        print("\n===== ChatGG Login =====")
        username = input("Usuário (bob/alice): ").lower()  # Solicita o nome do usuário
        password = input("Senha: ")  # Solicita a senha

        # Verifica se as credenciais estão corretas
        if username in usuarios and usuarios[username] == password:
            print(f"\nLogin bem-sucedido! Bem-vindo, {username.capitalize()}!")
            return username  # Retorna o nome do usuário
        else:
            print("\n[Erro] Usuário ou senha incorretos. Tente novamente.")

def on_message(ws, message):
    """
    Função que processa as mensagens recebidas do servidor WebSocket.
    """
    # Limpa a linha atual antes de exibir a nova mensagem
    sys.stdout.write("\r")
    sys.stdout.flush()
    
    # Verifica se a mensagem é uma notificação de entrada ou saída
    if "entrou no chat." in message or "saiu do chat." in message:
        print(f"\n{message}")  # Exibe a notificação
    else:
        try:
            # Tenta dividir a mensagem no formato "remetente: mensagem"
            remetente, mensagem_decifrada = message.split(':', 1)
            print(f"\n{remetente.strip()}: {mensagem_decifrada.strip()}")
        except ValueError:
            print(f"\n[Info] Mensagem recebida sem formato esperado: {message}")
    
    # Reimprime o prompt para o usuário após receber uma mensagem
    print("Você: ", end="", flush=True)

def on_error(ws, error):
    """
    Função que lida com erros de conexão WebSocket.
    """
    print(f"[Erro] Ocorreu um problema: {error}")

def on_close(ws, close_status_code, close_msg):
    """
    Função que lida com o encerramento da conexão WebSocket.
    """
    print(f"[Info] Conexão encerrada.")

def on_open(ws, remetente):
    """
    Função executada quando a conexão WebSocket é estabelecida.
    Envia o nome do remetente para o servidor.
    """
    print("\n[Info] Conectado ao ChatGG. Você pode começar a enviar mensagens.")
    print("[Info] Para sair do chat, digite 'sair' ou use o comando 'Ctrl + C'.\n")
    ws.send(remetente)  # Envia o nome do remetente assim que a conexão é aberta
    print("Você: ", end="", flush=True)

def send_messages(ws, remetente):
    """
    Função para enviar mensagens na thread principal.
    """
    try:
        while True:
            message = input()  # Captura a mensagem a ser enviada
            if message.lower() == 'sair':
                print("\n\n[Info] Você saiu do chat.")
                ws.close()  # Fecha a conexão
                break

            # Cifra a mensagem antes de enviá-la
            mensagem_cifrada = cipher_suite.encrypt(message.encode()).decode()  # Cifra a mensagem
            ws.send(f"[{datetime.now().strftime('%d/%m/%Y %H:%M')}] {remetente}: {mensagem_cifrada}")
            # Reimprime o prompt após o envio da mensagem
            print("Você: ", end="", flush=True)
            
    except KeyboardInterrupt:
        print("\n\n[Info] Você encerrou a conexão.")
        ws.close()

def main():
    """
    Função principal que realiza o login e gerencia a conexão WebSocket.
    """
    remetente = login()  # Solicita login do usuário

    # Conecta ao servidor WebSocket
    ws = websocket.WebSocketApp(websocket_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    # Passa o remetente para a função on_open
    def on_open_with_remetente(ws):
        on_open(ws, remetente)

    ws.on_open = on_open_with_remetente

    # Inicia a conexão WebSocket em uma nova thread
    wst = threading.Thread(target=ws.run_forever)
    wst.start()

    # Envia mensagens na thread principal
    send_messages(ws, remetente)

if __name__ == "__main__":
    main()  # Executa a função principal se o script for chamado diretamente