📧 Classificador de E-mails Inteligente
Este projeto é uma aplicação web simples desenvolvida com Flask que permite classificar o conteúdo de e-mails (via texto colado ou upload de arquivos .txt / .pdf) como "Produtivo" ou "Improdutivo". Além disso, ele utiliza a API do Hugging Face para realizar uma análise de sentimento do texto e gera uma sugestão de resposta.

✨ Funcionalidades
Classificação de E-mails: Categoriza e-mails como "Produtivos" (relacionados a trabalho, finanças, etc.) ou "Improdutivos" (spam, marketing, promoções).

Extração de Texto: Suporte para upload de arquivos .txt e .pdf para extração automática do conteúdo.

Análise de Sentimento: Integração com a API do Hugging Face para determinar o sentimento geral do e-mail (positivo, negativo, neutro).

Sugestão de Resposta: Gera uma resposta automática com base na categoria do e-mail.

Interface Web Amigável: Uma interface de usuário simples e responsiva construída com Tailwind CSS.

🚀 Como Começar
Siga os passos abaixo para configurar e executar o projeto em sua máquina local.

Pré-requisitos
Certifique-se de ter o Python 3.8+ e pip instalados.

1. Clonar o Repositório (se aplicável)
Se este código estiver em um repositório Git, clone-o:

git clone <URL_DO_SEU_REPOSITORIO>
cd <nome_do_seu_repositorio>

Se você tem apenas os arquivos, navegue até o diretório do projeto.

2. Criar e Ativar um Ambiente Virtual
É uma boa prática usar ambientes virtuais para gerenciar as dependências do projeto:

python -m venv venv
# No Windows
.\venv\Scripts\activate
# No macOS/Linux
source venv/bin/activate

3. Instalar as Dependências
Com o ambiente virtual ativado, instale as bibliotecas necessárias:

pip install Flask python-dotenv huggingface_hub pypdf werkzeug

4. Configurar Variáveis de Ambiente
Crie um arquivo chamado .env na raiz do seu projeto (na mesma pasta do app.py) e adicione as seguintes variáveis:

FLASK_SECRET_KEY=sua_chave_secreta_aqui_para_flash_messages
HF_API_TOKEN=seu_token_api_do_hugging_face_aqui
EMAIL_SIGNATURE=Atenciosamente,\nEquipe de Suporte Inteligente
PORT=5000

FLASK_SECRET_KEY: Uma string aleatória e segura para o Flask gerenciar sessões e mensagens flash.

HF_API_TOKEN: Você pode obter um token de API gratuito após se registrar no Hugging Face. Este token é necessário para a análise de sentimento.

EMAIL_SIGNATURE: A assinatura padrão para as respostas geradas. \n cria uma quebra de linha.

PORT: A porta na qual o servidor Flask será executado (padrão é 5000).

5. Executar a Aplicação
Com todas as dependências instaladas e as variáveis de ambiente configuradas, você pode iniciar o servidor Flask:

python app.py

Você verá uma saída no terminal indicando que o servidor está rodando, geralmente em http://127.0.0.1:5000/.

6. Acessar no Navegador
Abra seu navegador web e visite:

http://127.0.0.1:5000/

Você verá a interface do Classificador de E-mails Inteligente, onde poderá colar o texto de um e-mail ou carregar um arquivo .txt ou .pdf para análise.

⚙️ Estrutura do Projeto
app.py: O arquivo principal da aplicação Flask, contendo todas as rotas, lógica de classificação, extração de texto e integração com a API do Hugging Face.

.env: (Não incluído no controle de versão) Arquivo para armazenar variáveis de ambiente sensíveis.

requirements.txt: (Opcional, mas recomendado) Lista as dependências do projeto para fácil instalação.

📝 Palavras-chave de Classificação
O classificador utiliza as seguintes palavras-chave para determinar a categoria do e-mail:

Palavras Produtivas:
reunião, orçamento, contrato, pagamento, invoice, proposal, delivery, agenda

Palavras Improdutivas:
promoção, oferta, cupom, desconto, newsletter, unsubscribe, marketing

Você pode facilmente modificar essas listas no arquivo app.py para adaptar a classificação às suas necessidades.
