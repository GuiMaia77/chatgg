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


def cifrar_mensagem(mensagem: str, chave: bytes) -> str:
    fernet = Fernet(chave)
    mensagem_cifrada = fernet.encrypt(mensagem.encode())
    return mensagem_cifrada.decode()


def decifrar_mensagem(mensagem_cifrada: str, chave: bytes) -> str:
    fernet = Fernet(chave)
    mensagem_decifrada = fernet.decrypt(mensagem_cifrada.encode())
    return mensagem_decifrada.decode()


from pymongo import MongoClient

def conectar_mongodb():
    client = MongoClient('mongodb+srv://sinuquinha:12345678G@cluster0.3rhxm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    
    # Acesse o banco de dados
    db = client['chat_db']  # Nome do banco de dados (será criado se não existir)
    
    # Acesse a coleção
    colecao = db['mensagens']  # Nome da coleção
    return colecao



def inserir_mensagem(senha: str, mensagem: str):
    # Gerar salt e chave
    salt = os.urandom(16)
    chave = gerar_chave(senha, salt)

    # Cifrar mensagem
    mensagem_cifrada = cifrar_mensagem(mensagem, chave)

    colecao = conectar_mongodb()
    colecao.insert_one({
        'mensagem_cifrada': mensagem_cifrada,
        'salt': base64.b64encode(salt).decode()  # Armazenar o salt em base64
    })
    print("Mensagem criptografada inserida no MongoDB.")


def buscar_mensagem(senha: str):
    # Conectar ao MongoDB e recuperar a mensagem
    colecao = conectar_mongodb()
    documento = colecao.find_one()  # Buscar o primeiro documento (para simplificar)

    if documento:
        # Extrair mensagem e salt do documento
        mensagem_cifrada = documento['mensagem_cifrada']
        salt = base64.b64decode(documento['salt'])

        # Gerar chave com a mesma senha e salt
        chave = gerar_chave(senha, salt)

        # Decifrar a mensagem
        mensagem_decifrada = decifrar_mensagem(mensagem_cifrada, chave)
        return mensagem_decifrada
    else:
        print("Nenhuma mensagem encontrada.")
        return None

# Exemplo de uso
senha = "senha_segura"
mensagem = "Olá, Alice! Esta é uma mensagem secreta."

# Inserir mensagem no MongoDB
inserir_mensagem(senha, mensagem)

# Recuperar e decifrar mensagem
mensagem_recuperada = buscar_mensagem(senha)
print(f"Mensagem recuperada e decifrada: {mensagem_recuperada}")
