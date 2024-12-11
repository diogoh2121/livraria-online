from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

# Configuração do Flask
app = Flask(__name__)

# Configuração do SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///livraria.db'  # Nome do banco de dados
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializando o banco de dados
db = SQLAlchemy(app)

# Diretórios para upload
UPLOAD_FOLDER_LIVROS = 'uploads/livros'
UPLOAD_FOLDER_IMAGENS = 'uploads/imagens'
app.config['UPLOAD_FOLDER_LIVROS'] = UPLOAD_FOLDER_LIVROS
app.config['UPLOAD_FOLDER_IMAGENS'] = UPLOAD_FOLDER_IMAGENS

# Tipos de arquivos permitidos
ALLOWED_PDF_EXTENSIONS = {'pdf'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png'}
ALLOWED_EPUB_EXTENSIONS = {'epub'}

# Modelo para o banco de dados
class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    arquivo = db.Column(db.String(200), nullable=False)
    capa = db.Column(db.String(200), nullable=False)

# Função para verificar se o arquivo tem a extensão permitida
def allowed_file(filename, file_type):
    if file_type == 'pdf':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_PDF_EXTENSIONS
    if file_type == 'image':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    if file_type == 'epub':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EPUB_EXTENSIONS
    return False

# Rota principal - Página inicial
@app.route('/')
def index():
    livros = Livro.query.all()
    return render_template('index.html', livros=livros)

# Rota para servir arquivos de livros
@app.route('/livros/<nome_arquivo>')
def servir_livro(nome_arquivo):
    return send_from_directory(app.config['UPLOAD_FOLDER_LIVROS'], nome_arquivo)

# Rota para servir imagens das capas
@app.route('/imagens/<nome_arquivo>')
def servir_imagem(nome_arquivo):
    return send_from_directory(app.config['UPLOAD_FOLDER_IMAGENS'], nome_arquivo)

# Rota para adicionar livros
@app.route('/adicionar_livro', methods=['GET', 'POST'])
def adicionar_livro():
    if request.method == 'POST':
        nome_livro = request.form['nome']
        arquivo_pdf = request.files.get('pdf')
        arquivo_epub = request.files.get('epub')
        capa_imagem = request.files.get('capa')

        # Validar e salvar o PDF ou EPUB
        if arquivo_pdf and allowed_file(arquivo_pdf.filename, 'pdf') and capa_imagem and allowed_file(capa_imagem.filename, 'image'):
            nome_arquivo_pdf = secure_filename(arquivo_pdf.filename)
            caminho_pdf = os.path.join(app.config['UPLOAD_FOLDER_LIVROS'], nome_arquivo_pdf)
            arquivo_pdf.save(caminho_pdf)

            nome_arquivo_capa = secure_filename(capa_imagem.filename)
            caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER_IMAGENS'], nome_arquivo_capa)
            capa_imagem.save(caminho_imagem)

            novo_livro = Livro(nome=nome_livro, arquivo=nome_arquivo_pdf, capa=nome_arquivo_capa)
            db.session.add(novo_livro)
            db.session.commit()

        elif arquivo_epub and allowed_file(arquivo_epub.filename, 'epub') and capa_imagem and allowed_file(capa_imagem.filename, 'image'):
            nome_arquivo_epub = secure_filename(arquivo_epub.filename)
            caminho_epub = os.path.join(app.config['UPLOAD_FOLDER_LIVROS'], nome_arquivo_epub)
            arquivo_epub.save(caminho_epub)

            nome_arquivo_capa = secure_filename(capa_imagem.filename)
            caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER_IMAGENS'], nome_arquivo_capa)
            capa_imagem.save(caminho_imagem)

            novo_livro = Livro(nome=nome_livro, arquivo=nome_arquivo_epub, capa=nome_arquivo_capa)
            db.session.add(novo_livro)
            db.session.commit()

        return redirect(url_for('index'))

    return render_template('adicionar_livro.html')

# Inicializar o servidor e criar tabelas, se necessário
if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER_LIVROS, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER_IMAGENS, exist_ok=True)

    # Criar tabelas no banco de dados dentro do contexto da aplicação
    with app.app_context():
        db.create_all()

    app.run(debug=True)
