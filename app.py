import json
import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import CSRFProtect, CSRFError
import datetime

app = Flask(__name__)
app.secret_key = 'b968edbd35bc918de1885b84036d9607aa157de2697811d2'
csrf = CSRFProtect(app)

class UploadForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired(), URL()])
    name = StringField('Nome', validators=[DataRequired()])
    description = StringField('Descrição', validators=[DataRequired()])
    size = StringField('Tamanho do arquivo', validators=[DataRequired()])
    link_type = SelectField('Tipo de link', choices=[
        ('mega', 'Mega'),
        ('mediafire', 'Mediafire'),
        ('torrent', 'Torrent'),
        ('pdf', 'PDF'),
        ('zip', 'ZIP'),
        ('onion', 'Onion'),
        ('url', 'URL'),  
        ('outro', 'Outro')
    ], validators=[DataRequired()])
    category = SelectField('Categoria', choices=[
        ('sites', 'Sites'), 
        ('pornografia', 'Pornografia'),
        ('gore', 'Gore'),  # Categoria adicionada
        ('metodos', 'Métodos'),
        ('apk', 'APK'),
        ('cursos', 'Cursos'),
        ('outro', 'Outro')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Enviar')

def load_urls():
    try:
        with open('urls.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON em urls.json: {e}")
        return []

def save_url(data):
    try:
        with open('urls.json', 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Erro ao salvar URLs: {e}")

def log_event(action, ip, details=None):
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "ip": ip,
        "action": action
    }
    if details:
        log_entry["details"] = details
    try:
        with open('logs.json', 'a') as log_file:
            log_file.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Erro ao registrar evento: {e}")

def get_client_ip():
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    return request.remote_addr

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    selected_category = request.args.get('category', '').strip()
    log_event(f"Search attempted with query: {query}", get_client_ip())
    if not query:
        return redirect(url_for('index'))
    urls = load_urls()
    if selected_category:
        results = [url for url in urls if url['category'] == selected_category]
    else:
        results = [url for url in urls 
                   if (query.lower() in url['name'].lower() or query.lower() in url['description'].lower())]
    total_results = len(results)
    return render_template('results.html', query=query, results=results, total_results=total_results)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        url = form.url.data
        name = form.name.data
        description = form.description.data
        size = form.size.data
        link_type = form.link_type.data
        category = form.category.data
        if not is_valid_url(url):
            log_event(f"Invalid URL attempted: {url}", get_client_ip())
            return render_template('upload.html', form=form, error="URL inválida. Por favor, insira uma URL válida.")
        urls = load_urls()
        urls.append({
            "url": url,
            "name": name,
            "description": description,
            "size": size,
            "link_type": link_type,
            "category": category
        })
        save_url(urls)
        log_event("Upload realizado", get_client_ip(), {
            "url": url,
            "name": name,
            "description": description,
            "size": size,
            "link_type": link_type,
            "category": category
        })
        return redirect(url_for('index'))
    return render_template('upload.html', form=form)

def is_valid_url(url):
    return requests.utils.urlparse(url).scheme in ["http", "https"]

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', message=e.description), 400

@app.errorhandler(404)
def page_not_found(e):
    log_event("404 Not Found", get_client_ip())
    return render_template('not_found.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
