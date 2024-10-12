import asyncio
import websockets
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
import certifi
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Obtém a chave de criptografia e a string de conexão do MongoDB do ambiente
KEY = os.getenv('KEY')
MONGO_URI = os.getenv('MONGO_URI')

# Validação da chave de criptografia
if not KEY:
    raise ValueError("Chave de criptografia não definida no arquivo .env")

# Certificado CA para a conexão segura com MongoDB
ca = certifi.where()

# Variável global para o cliente MongoDB
mongo_client = None

# Inicializa o conjunto de cifras (cipher suite) com a chave carregada
cipher_suite = Fernet(KEY.encode())  # Certifique-se de codificar para bytes

# Dicionário para armazenar o nome de cada cliente associado ao websocket
client_names = {}

# Lista para armazenar clientes conectados
connected_clients = set()

# Função assíncrona para conectar ao MongoDB
async def conectar_mongodb():
    global mongo_client
    try:
        mongo_client = MongoClient(
            MONGO_URI,
            tlsCAFile=ca,
            serverSelectionTimeoutMS=10000  # Aumenta o tempo de espera para 10 segundos
        )
        mongo_client.admin.command('ping')  # Testa a conexão com o MongoDB
        print("Conectado ao MongoDB com sucesso!")
    except ConnectionFailure:
        print("Falha na conexão com o MongoDB.")
        raise  # Levanta a exceção para encerrar o servidor
    except PyMongoError as e:
        print(f"Erro ao conectar ao MongoDB: {e}")

# Função que gerencia a comunicação com o WebSocket
async def handle_connection(websocket, path):
    if mongo_client is None:
        print("Conexão com o MongoDB não estabelecida. Encerrando...")
        return

    colecao_mensagens = mongo_client['chat_db']['mensagens']  # Seleciona a coleção de mensagens no MongoDB
    
    try:
        # Recebe a primeira mensagem do cliente, que deve ser o nome do usuário
        nome_cliente = await websocket.recv()
        client_names[websocket] = nome_cliente  # Armazena o nome do cliente
        connected_clients.add(websocket)  # Adiciona o cliente à lista de conectados

        # Descomente se quiser ver os clientes que se conectaram
        # print(f"{nome_cliente} conectado com sucesso!")

        # Notifica todos os outros clientes que um novo usuário se conectou
        join_message = f"{nome_cliente} entrou no chat."
        for client in connected_clients:
            if client != websocket:
                await client.send(join_message)

        async for message in websocket:
            # Descomente se quiser ver as mensagens trocadas no servidor
            # print(f"Mensagem recebida de {nome_cliente}: {message}")
            try:
                # Divide a mensagem em remetente e mensagem cifrada
                remetente, mensagem_cifrada = message.split(': ', 1)

                # Salva a mensagem cifrada no MongoDB
                mensagem_cifrada_salva = colecao_mensagens.insert_one({
                    'de': remetente,
                    'mensagem_cifrada': mensagem_cifrada
                })
                # Descomente se quiser ver as mensagens sendo salvas corretamente no MongoDB
                # print("Mensagem cifrada salva no MongoDB com sucesso!")

                # Busca a mensagem cifrada
                mensagem_cifrada_banco = colecao_mensagens.find_one({"_id": mensagem_cifrada_salva.inserted_id})

                # Decifra a mensagem para enviá-la aos outros usuários
                mensagem_decifrada = cipher_suite.decrypt(mensagem_cifrada_banco['mensagem_cifrada'].encode()).decode()
                mensagem_completa = f"{remetente}: {mensagem_decifrada}"

            except (ValueError, PyMongoError) as e:
                print(f"Erro ao processar a mensagem: {e}")
                continue  # Continua para a próxima iteração em caso de erro
            except Exception as e:
                print(f"Erro ao decifrar mensagem: {e}")
                continue  # Continua para a próxima iteração em caso de erro

            # Envia a mensagem decifrada para todos os outros clientes conectados
            for client in connected_clients:
                if client != websocket:
                    await client.send(mensagem_completa)

    finally:
        # Remove o cliente da lista de conectados ao desconectar
        connected_clients.remove(websocket)
        disconnect_message = f"{nome_cliente} saiu do chat."
        for client in connected_clients:
            await client.send(disconnect_message)  # Notifica os outros clientes da desconexão

        # Descomente se quiser ver os clientes que se desconectou
        # print(f"{nome_cliente} desconectado.")  # Exibe o nome do cliente que se desconectou
        del client_names[websocket]  # Remove o nome do cliente ao desconectar

# Função principal para iniciar o servidor WebSocket
async def main():
    await conectar_mongodb()  # Conecta ao MongoDB antes de iniciar o servidor
    async with websockets.serve(handle_connection, "localhost", 8765):
        print("Servidor WebSocket iniciado na porta 8765...")
        await asyncio.Future()  # Mantém o servidor ativo

# Iniciar o servidor
if __name__ == "__main__":
    asyncio.run(main())