from flask import Flask, request, render_template_string, redirect, url_for, flash, get_flashed_messages
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from pypdf import PdfReader
import os

print("🔹 Carregando variáveis de ambiente...")
load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key-fallback-if-not-set")
ALLOWED_EXTENSIONS = {"txt", "pdf"}

print("🔹 Flask inicializado com sucesso!")

# ---------------- HTML da Página Principal ----------------
# Este é o HTML completo que será renderizado pela sua aplicação Flask.
# Ele inclui Tailwind CSS para um design moderno e responsivo, e um indicador de carregamento.
PAGE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Classificador de E-mails</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f3f4f6;
        }
        .container {
            max-width: 800px;
            margin: 2rem auto;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            padding: 2.5rem;
            animation: fadeIn 0.8s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .flash-message {
            padding: 0.75rem 1.25rem;
            margin-bottom: 1rem;
            border-radius: 0.5rem;
            color: #fff;
            font-weight: 600;
        }
        .flash-error {
            background-color: #ef4444; /* red-500 */
        }
        .flash-success {
            background-color: #22c55e; /* green-500 */
        }
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            visibility: hidden;
            opacity: 0;
            transition: opacity 0.3s ease-in-out;
        }
        .loading-overlay.visible {
            visibility: visible;
            opacity: 1;
        }
        .loader {
            border: 6px solid #f3f3f3;
            border-top: 6px solid #3b82f6; /* blue-500 */
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center">
    <div class="container">
        <h1 class="text-4xl font-extrabold text-center text-gray-800 mb-8 tracking-tight">
            Analisador de E-mails Inteligente
        </h1>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="mb-6">
                    {% for category, message in messages %}
                        <div class="flash-message {% if category == 'error' %}flash-error{% elif category == 'success' %}flash-success{% endif %}">
                            {{ message }}
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}

        <form action="{{ url_for('classify') }}" method="post" enctype="multipart/form-data" class="space-y-6" onsubmit="showLoading()">
            <div>
                <label for="email_text" class="block text-lg font-semibold text-gray-700 mb-2">
                    Cole o conteúdo do e-mail aqui:
                </label>
                <textarea id="email_text" name="email_text" rows="8"
                          class="w-full p-4 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 transition duration-200 ease-in-out"
                          placeholder="Ex: 'Olá, gostaria de confirmar a reunião agendada para amanhã às 10h.'"></textarea>
            </div>

            <div class="flex items-center justify-center text-gray-600 font-medium">
                — OU —
            </div>

            <div>
                <label for="email_file" class="block text-lg font-semibold text-gray-700 mb-2">
                    Carregue um arquivo (.txt ou .pdf):
                </label>
                <input type="file" id="email_file" name="email_file" accept=".txt, .pdf"
                       class="w-full text-gray-700 bg-white border border-gray-300 rounded-lg shadow-sm
                              file:mr-4 file:py-3 file:px-6 file:rounded-lg file:border-0
                              file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700
                              hover:file:bg-blue-100 cursor-pointer transition duration-200 ease-in-out"/>
                <p class="text-sm text-gray-500 mt-2">Formatos permitidos: .txt, .pdf</p>
            </div>

            <div class="flex justify-center">
                <button type="submit"
                        class="px-8 py-4 bg-blue-600 text-white font-bold rounded-lg shadow-lg
                               hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300
                               transition duration-300 ease-in-out transform hover:scale-105">
                    Classificar E-mail
                </button>
            </div>
        </form>

        {% if result %}
            <div class="mt-10 p-6 bg-blue-50 border border-blue-200 rounded-xl shadow-md space-y-4 animate-fadeIn">
                <h2 class="text-3xl font-bold text-blue-800 mb-4 text-center">Resultado da Análise</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <p class="text-lg text-blue-700 font-semibold">Categoria:</p>
                        <p class="text-xl text-gray-800">{{ result.category }}</p>
                    </div>
                    <div>
                        <p class="text-lg text-blue-700 font-semibold">Motivo:</p>
                        <p class="text-xl text-gray-800">{{ result.reason }}</p>
                    </div>
                    <div>
                        <p class="text-lg text-blue-700 font-semibold">Sentimento (Hugging Face):</p>
                        <p class="text-xl text-gray-800">{{ result.sentiment }} (Confiança: {{ "%.2f"|format(result.confidence * 100) }}%)</p>
                    </div>
                </div>
                <div class="mt-6 border-t border-blue-200 pt-4">
                    <p class="text-lg text-blue-700 font-semibold mb-2">Sugestão de Resposta:</p>
                    <textarea readonly rows="6"
                              class="w-full p-4 bg-white border border-blue-300 rounded-lg text-gray-800
                                     focus:outline-none resize-none">{{ result.reply }}</textarea>
                </div>
            </div>
        {% endif %}
    </div>

    <div class="loading-overlay" id="loadingOverlay">
        <div class="loader"></div>
        <p class="ml-4 text-xl text-blue-700 font-semibold">Analisando...</p>
    </div>

    <script>
        function showLoading() {
            document.getElementById('loadingOverlay').classList.add('visible');
        }
        // Hide loading overlay if page reloads (e.g., due to flash messages)
        window.onload = function() {
            document.getElementById('loadingOverlay').classList.remove('visible');
        };
    </script>
</body>
</html>
"""

# ---------------- Funções utilitárias ----------------
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(fp) -> str:
    print("🔹 Extraindo texto do PDF...")
    try:
        reader = PdfReader(fp)
        # Junta todas as páginas, lidando com páginas vazias
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    except Exception as e:
        print(f"❌ Erro ao extrair PDF: {e}")
        return ""

POSITIVE_KEYWORDS = ["reunião", "orçamento", "contrato", "pagamento", "invoice", "proposal", "delivery", "agenda"]
NEGATIVE_KEYWORDS = ["promoção", "oferta", "cupom", "desconto", "newsletter", "unsubscribe", "marketing"]

def classify_email(text: str):
    print("🔹 Classificando email...")
    low = text.lower()
    score_pos = sum(1 for k in POSITIVE_KEYWORDS if k in low)
    score_neg = sum(1 for k in NEGATIVE_KEYWORDS if k in low)
    
    reason_details = []
    if score_pos > 0:
        detected_pos = [k for k in POSITIVE_KEYWORDS if k in low]
        reason_details.append(f"Palavras produtivas: {', '.join(detected_pos)}")
    if score_neg > 0:
        detected_neg = [k for k in NEGATIVE_KEYWORDS if k in low]
        reason_details.append(f"Palavras improdutivas: {', '.join(detected_neg)}")

    reason = "; ".join(reason_details) if reason_details else "Nenhuma palavra-chave específica detectada."

    if score_pos > score_neg:
        return "Produtivo", reason
    if score_neg > score_pos:
        return "Improdutivo", reason
    
    # Caso os scores sejam iguais, tenta uma classificação padrão
    return "Produtivo", "Conteúdo informativo sem sinais fortes de spam ou marketing."


DEFAULT_SIGNATURE = os.getenv("EMAIL_SIGNATURE", "Atenciosamente,\nEquipe de Suporte")

def generate_reply(category: str, text: str) -> str:
    if category == "Produtivo":
        return f"Olá,\n\nObrigado pelo contato. Recebemos sua mensagem e retornaremos em breve com as informações solicitadas.\n\n{DEFAULT_SIGNATURE}"
    else:
        return f"Olá,\n\nAgradecemos o contato. No momento, não temos interesse em ofertas promocionais ou newsletters. Para cancelar futuras comunicações, por favor, clique aqui.\n\n{DEFAULT_SIGNATURE}"

def analyze_sentiment_with_huggingface(text: str):
    print("🔹 Enviando texto para Hugging Face API...")
    # Limita o texto para evitar exceder o limite de tokens da API do Hugging Face
    # Muitos modelos têm limite de 512 tokens, 2000 caracteres é uma estimativa segura.
    text_for_hf = text[:2000] 
    try:
        client = InferenceClient(token=os.getenv("HF_API_TOKEN"))
        # Usando um modelo de classificação de sentimento em português, se disponível e preferível.
        # Caso contrário, 'distilbert-base-uncased-finetuned-sst-2-english' é um bom fallback para inglês.
        # Para português, você pode tentar 'nlptown/bert-base-multilingual-uncased-sentiment'
        model = "distilbert-base-uncased-finetuned-sst-2-english" # Mantenha este se o conteúdo for primariamente em inglês
        # model = "nlptown/bert-base-multilingual-uncased-sentiment" # Descomente e use este se o conteúdo for em português

        response = client.text_classification(inputs=text_for_hf, model=model)
        
        # A resposta pode ser uma lista de dicionários, pegamos o primeiro
        if response and isinstance(response, list) and len(response) > 0:
            label = response[0]["label"]
            confidence = response[0]["score"]
            print(f"🔹 Sentimento retornado: {label} (Confiança: {confidence:.2f})")
            return label, confidence
        else:
            print("❌ Resposta inesperada da API Hugging Face.")
            return "Indefinido", 0.0

    except Exception as e:
        print(f"❌ Erro ao analisar sentimento com Hugging Face: {e}")
    
        return "Erro na Análise", 0.0

# ---------------- Rotas ----------------
@app.route("/", methods=["GET"])
def index():
    print("🔹 Rota / acessada")
    # Limpa as mensagens flash em um novo carregamento da página
    # Use get_flashed_messages() para consumir as mensagens
    _ = list(get_flashed_messages()) 
    return render_template_string(PAGE, result=None)

@app.route("/classify", methods=["POST"])
def classify():
    print("🔹 Recebendo submissão de email...")
    text = ""
    file = request.files.get("email_file")

    if file and file.filename and allowed_file(file.filename):
        ext = file.filename.rsplit(".", 1)[1].lower()
        print(f"🔹 Arquivo recebido: {file.filename} ({ext})")
        
        # Para garantir que o arquivo seja lido corretamente, salve-o temporariamente ou use BytesIO
        # Aqui, passando o objeto de arquivo diretamente para pypdf (que aceita file-like objects)
        if ext == "txt":
            text = file.read().decode("utf-8", errors="ignore")
        elif ext == "pdf":
            text = extract_text_from_pdf(file)
    
    # Se não houver arquivo ou o arquivo estiver vazio, tenta pegar do textarea
    if not text:
        text = request.form.get("email_text", "").strip()
        if text:
            print("🔹 Texto vindo do textarea")
    
    if not text:
        flash("Por favor, forneça um arquivo ou cole o texto do e-mail para classificar.", "error")
        print("❌ Nenhum texto fornecido")
        return redirect(url_for("index"))

    category, reason = classify_email(text)
    reply = generate_reply(category, text)
    sentiment, confidence = analyze_sentiment_with_huggingface(text)

    result = {
        "category": category,
        "reason": reason,
        "reply": reply,
        "sentiment": sentiment,
        "confidence": confidence
    }
    print("🔹 Resultado preparado, retornando para HTML")
    return render_template_string(PAGE, result=result)

# ---------------- Rodar Aplicação ----------------
if __name__ == "__main__":
    print("🔹 Rodando Flask na porta 5000...")
    # Em produção, você usaria um servidor WSGI como Gunicorn.
    # Para desenvolvimento, debug=True é útil para recarga automática.
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
