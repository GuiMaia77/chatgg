from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import os
from pymongo import MongoClient

# Função para gerar chave com senha e salt
def gerar_chave(senha: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    chave = base64.urlsafe_b64encode(kdf.derive(senha.encode()))
    return chave

# Função para combinar uma chave simétrica
def combinar_chave_simetrica(senha: str, salt: bytes) -> bytes:
    chave = gerar_chave(senha, salt)
    return chave

# Função para criptografar mensagem
def cypher(mensagem: str, chave: bytes) -> str:
    fernet = Fernet(chave)
    mensagem_cifrada = fernet.encrypt(mensagem.encode())
    return mensagem_cifrada.decode()

# Função para descriptografar mensagem
def decrypt(mensagem_cifrada: str, chave: bytes) -> str:
    fernet = Fernet(chave)
    mensagem_decifrada = fernet.decrypt(mensagem_cifrada.encode())
    return mensagem_decifrada.decode()

# Função para conectar ao MongoDB
def conectar_mongodb():
    client = MongoClient('mongodb+srv://sinuquinha:12345678G@cluster0.3rhxm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    db = client['chat_db']  # Nome do banco de dados
    return db

# Usuários pré-cadastrados
USUARIOS_PRE_CADASTRADOS = {
    'alice': 'senha_segura',
    'bob': 'senha_bob'  # Nova senha para Bob
}

# Função para inserir mensagem com remetente e destinatário
def inserir_mensagem(remetente: str, para: str, senha: str, mensagem: str):
    db = conectar_mongodb()
    colecao_mensagens = db['mensagens']

    salt = os.urandom(16)
    chave = combinar_chave_simetrica(senha, salt)

    # Cifrar mensagem
    mensagem_cifrada = cypher(mensagem, chave)

    # Inserir mensagem cifrada no MongoDB
    colecao_mensagens.insert_one({
        'de': remetente,
        'para': para,
        'mensagem_cifrada': mensagem_cifrada,
    })
    print("Mensagem criptografada inserida no MongoDB.")


def buscar_mensagem(de: str, para: str, senha: str):
    db = conectar_mongodb()
    colecao_mensagens = db['mensagens']

    # Busca específica entre remetente e destinatário
    documento = colecao_mensagens.find_one({'de': de, 'para': para})

    if documento:
        mensagem_cifrada = documento['mensagem_cifrada']
        salt = base64.b64decode(documento['salt'])
        chave = combinar_chave_simetrica(senha, salt)
        mensagem_decifrada = decrypt(mensagem_cifrada, chave)
        return mensagem_decifrada
    else:
        print("Nenhuma mensagem encontrada.")
        return None


def login():
    nome = input("Digite seu nome de usuário (alice ou bob): ")
    senha = input("Digite sua senha: ")

    
    if nome in USUARIOS_PRE_CADASTRADOS and senha == USUARIOS_PRE_CADASTRADOS[nome]:
        print("\nLogin bem-sucedido!")
        return nome  
    else:
        print("\nUsuário ou senha incorretos. Tente novamente.")
        return None

# Função principal para interagir com o usuário
def main():
    print("--- Bem-vindo ao sistema de mensagens criptografadas ---")
    
    usuario_logado = None
    while usuario_logado is None:
        usuario_logado = login()
    
    senha_usuario = USUARIOS_PRE_CADASTRADOS[usuario_logado]

    while True:
        print("\n--- Menu ---")
        print(f"Usuário logado: {usuario_logado}")
        print("1. Enviar mensagem")
        print("2. Buscar mensagem")
        print("3. Sair")
        escolha = input("Escolha uma opção (1/2/3): ")

        if escolha == '1':
            para = input("Digite o nome do destinatário: ")
            senha_combinada = input("Digite a senha combinada: ")
            mensagem = input("Digite a mensagem: ")
            inserir_mensagem(usuario_logado, para, senha_combinada, mensagem)

        elif escolha == '2':
            de = input("Digite o nome do remetente: ")  # Inserir o remetente
            senha_combinada = input("Digite a senha combinada: ")
            mensagem_recuperada = buscar_mensagem(de, usuario_logado, senha_combinada)
            if mensagem_recuperada:
                print(f"Mensagem recuperada e decifrada: {mensagem_recuperada}")

        elif escolha == '3':
            print("Saindo...")
            break

        else:
            print("Opção inválida. Tente novamente.")

# Executar o programa
if __name__ == "__main__":
    main()
