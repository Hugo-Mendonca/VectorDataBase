# VectorDataBase
Projeto para cadeira de banco de dados


Parte Prática passo a passo


Pré-requisitos
Antes de iniciar, certifique-se de ter os seguintes softwares instalados em seu sistema:
Docker Desktop (para Windows/macOS) ou Docker Engine (para Linux). Você pode fazer o download e seguir as instruções de instalação em https://www.docker.com/products/docker-desktop/.
Python 3.x instalado.
Um editor de texto (como VS Code, Gedit, ou Nano) para editar arquivos de código.

1. Configurando o Ambiente Docker para o Qdrant
O Qdrant, nosso banco de dados vetorial, será executado dentro de um contêiner Docker.
1.1. Iniciando o Contêiner Docker do Qdrant
Abra seu terminal no Linux (ou Prompt de Comando/PowerShell no Windows) e execute o seguinte comando. Este comando baixará a imagem do Qdrant (se ainda não a tiver) e iniciará o serviço.

-p 6333:6333: Mapeia a porta da API HTTP (usada pelo dashboard) do contêiner para a porta 6333 do seu computador.
-p 6334:6334: Mapeia a porta da API gRPC (usada pelo cliente Python) do contêiner para a porta 6334 do seu computador.
-v $(pwd)/qdrant_storage:/qdrant/storage: Cria um volume de dados. Isso significa que os dados do Qdrant serão armazenados em uma pasta chamada qdrant_storage no diretório onde você executa este comando, garantindo que os dados persistam mesmo se o contêiner for reiniciado.
qdrant/qdrant: É o nome da imagem oficial do Qdrant no Docker Hub.
1.2. Lidando com Problemas de Credenciais GPG (Opcional, se ocorrer)
Durante a fase de configuração do Docker, pode ser que você encontre um pop-up solicitando uma "Frase Secreta" relacionada ao GPG (GNU Privacy Guard). Isso ocorre quando o Docker tenta usar um gerenciador de credenciais que depende de suas chaves GPG, e pode acontecer se a frase-secreta estiver incorreta ou a configuração não estiver ideal.

Solução: Uma forma de contornar isso é editar o arquivo de configuração do Docker (~/.docker/config.json) para que ele não use o credsStore problemático.
No terminal use o comando ~/.docker/config.json
Remova a linha "credsStore": "desktop", se ela estiver presente.(Deslocamento até a linha é através das setinhas)
Salve o arquivo e feche o editor(Cntrl+O e depois Cntrl +K) .
Tente fazer docker login novamente. O Docker deve, então, preferir o login via navegador ou pedir suas credenciais diretamente no terminal, sem o pop-up GPG.(Foi oq houve comigo, pediu confirmação via navegador que no caso foi só abrir o docker e confirmar)
1.3. Verificando o Dashboard do Qdrant
Após a execução bem-sucedida do comando docker run, o Qdrant estará ativo. Você pode verificar seu status e explorar as coleções através da interface web.
Abra seu navegador e acesse a URL: http://localhost:6333/dashboard
esse é um checkpoint importante para ver se ta tudo certo.



2. Preparando o Ambiente Python
Seu script Python interage com o Qdrant. Para gerenciar as dependências do Python de forma limpa, utilizaremos um ambiente virtual.(A ideia de isolar as dependências de um projeto é a prática recomendada em qualquer sistema operacional para evitar conflitos de pacotes. Que foi oq houve na minha máquina, não dava pra rodar sem o ambiente venv)
2.1. Criando o Ambiente Virtual
Navegue até o diretório do seu projeto (onde está o arquivo Teste_seminario.py) no terminal. Em seguida, execute o comando para criar um ambiente virtual chamado venv:
No terminal o camando:
python3 -m venv venv


2.2. Ativando o Ambiente Virtual
Após a criação, você precisa "ativar" o ambiente virtual. Isso garante que todos os pacotes Python que você instalar ou executar estarão isolados neste ambiente.
No terminal:
source venv/bin/activate


Você saberá que o ambiente virtual está ativo quando (venv) aparecer no início do seu prompt do terminal.
2.3. Instalando as Dependências Python
Com o ambiente virtual ativo, instale as bibliotecas necessárias para o seu script. No seu projeto, isso inclui qdrant-client para se comunicar com o Qdrant e sentence-transformers para gerar os embeddings de texto.
No terminal: 
pip install qdrant-client sentence-transformers
(Demora MUITO para instalar todas as bibliotecas, pelo menos para mim demorou papo de 30 minutos)


Dá para perceber que estamos no ambiente VENV pois no início temos o (VENV).

3. Executando o Script Python
Agora que o Qdrant está rodando no Docker e seu ambiente Python está configurado com as dependências, você pode executar o script Nome_do_seu_Arquivo.py.
Abra um novo terminal (mantendo o Qdrant rodando no primeiro terminal) e navegue novamente até o diretório do seu projeto. Certifique-se de que o ambiente virtual está ativo neste novo terminal também.
Bash
python3 Nome_do_seu_Arquivo.py

