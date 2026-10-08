O A.T.L.A.S. é um assistente de produtividade e foco desenvolvido em Python. Desenhado para maximizar o rendimento nos estudos, funciona como um cronômetro Pomodoro inteligente com integração nativa ao Spotify e um sistema de telemetria "caixa preta" que registra o seu tempo de foco localmente para análise de desempenho.

🚀 Funcionalidades

Cronômetro Dinâmico: Fila de tarefas onde você pode definir a matéria e o tempo exato (em minutos) para cada sessão de foco e descanso.

Integração Spotify: Controle sua playlist diretamente pela interface do aplicativo (iniciar, pausar, avançar) usando o Spotify em segundo plano.

Modo Visor Tático: A janela mantém-se sempre no topo (Always on Top), permitindo que você visualize o cronômetro enquanto lê PDFs ou utiliza outros softwares.

Telemetria de Estudos: Gravação silenciosa num banco de dados SQLite (atlas.db) sempre que você completa um bloco de estudos.

Painel Retrátil de Estatísticas: Visualização rápida das horas totais investidas em cada disciplina diretamente na tela principal, clicando no botão (#).

🛠️ Tecnologias Utilizadas

Flet: Framework para a interface gráfica (UI), permitindo que o código Python seja facilmente exportado para Web ou Mobile no futuro.

Spotipy: Biblioteca para integração e controle remoto da API do Spotify.

SQLite3: Banco de dados relacional leve e nativo do Python, utilizado para gravar a telemetria.

📦 Instalação e Pré-requisitos

O projeto utiliza bibliotecas nativas do Python (sqlite3, asyncio, datetime), mas requer a instalação de dois pacotes externos.

Certifique-se de que tem o Python 3 instalado.

Abra o terminal no seu projeto e instale as dependências utilizando o pip:

pip install flet spotipy


⚙️ Configuração do Spotify

Para que os botões de música funcionem, você precisa conectar o aplicativo à sua conta do Spotify for Developers:

Acesse o Spotify Developer Dashboard e crie um novo Web App.

Nas configurações do App no Spotify, defina o Redirect URI exatamente como: http://127.0.0.1:8888.

Copie o seu Client ID e Client Secret.

Abra o código fonte do A.T.L.A.S. e cole as suas chaves na seção de configuração do Spotify:

MEU_CLIENT_ID = "COLA_O_TEU_CLIENT_ID_AQUI"

MEU_CLIENT_SECRET = "COLA_O_TEU_CLIENT_SECRET_AQUI" 


▶️ Como Executar
Com as bibliotecas instaladas e as chaves configuradas, basta executar o script principal no terminal:
python atlas.py

(Nota: O aplicativo requer que o software oficial do Spotify esteja aberto no computador, mesmo que em segundo plano, para que exista um dispositivo ativo pronto para reproduzir a música).
