# ChatGG

**ChatGG** é um mini projeto acadêmico que implementa um sistema de chat em tempo real utilizando WebSockets e MongoDB. Desenvolvido em Python, o ChatGG inclui funcionalidades de criptografia para garantir a segurança das mensagens trocadas entre os usuários. Este projeto serve como uma base sólida para a construção de sistemas de chat mais robustos e escaláveis.

## Funcionalidades

- **Conexão em Tempo Real:** Permite comunicação instantânea entre usuários utilizando WebSockets.
- **Criptografia de Mensagens:** As mensagens enviadas são criptografadas, garantindo a privacidade da comunicação.
- **Armazenamento Seguro:** Mensagens cifradas são armazenadas no MongoDB, mantendo a integridade dos dados.
- **Notificações de Presença:** Notifica os usuários quando outros participantes entram ou saem do chat.

## Configuração

### Dependências

Para executar este projeto, você precisará do Python 3.x e das seguintes bibliotecas:

- `websockets`
- `pymongo`
- `cryptography`
- `python-dotenv`
- `certifi`

Instale as dependências necessárias utilizando o `pip`:

```bash
pip install websockets pymongo cryptography python-dotenv certifi
```

### Variáveis de Ambiente

> **Atenção:** Este projeto é uma demonstração acadêmica e, portanto, as credenciais do MongoDB e a chave de criptografia estão expostas no arquivo `.env`. Para utilizar este projeto como base para um sistema de chat real, recomenda-se seguir estas diretrizes:

1. Crie um arquivo `.env.example` e adicione as variáveis de ambiente necessárias, deixando os valores em branco.
2. Adicione o arquivo `.env` ao seu `.gitignore` para evitar problemas de segurança em produção.

Exemplo de um arquivo `.env`:

```
MONGO_URI="sua_string_do_mongo"
KEY="sua_chave_de_criptografia"
```

### Executando o Projeto

1. **Certifique-se de que o MongoDB está em execução.**
2. **Configure suas variáveis de ambiente** em um arquivo `.env`.
3. **Inicie o servidor WebSocket:**

   ```bash
   python server/server.py
   ```

4. **Inicie o cliente de chat:**

   ```bash
   python client/client.py
   ```

5. **Para ver o chat funcionando:** Você pode abrir outro cliente com o passo 4 e fazer login com outro usuário (as credenciais podem ser encontradas no arquivo `arqv-login.txt`) e trocar mensagens.

## Contribuição

Sinta-se à vontade para usar este projeto como base para desenvolver seus próprios sistemas de chat. Para desenvolvedores que desejam expandir o ChatGG, uma excelente ideia seria criar uma interface web interativa que se conecte ao servidor WebSocket em Python, proporcionando uma experiência de usuário mais agradável e moderna. 

## Dicas para Adicionar o `.gitignore`

Crie um arquivo chamado `.gitignore` na raiz do seu projeto e adicione a seguinte linha para garantir que o arquivo `.env` não seja rastreado pelo Git:

```
.env
```

## Desenvolvedores

Gabriel Cardoso Lima:
- [GitHub](https://github.com/GabrielCardosoLIma)

Guilherme Maia Dias:
- [GitHub](https://github.com/GuiMaia77)