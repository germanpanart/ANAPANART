# ═══════════════════════════════════════════════════════════════════════
#  app.py — Servidor Flask · Plataforma Jurídica Dra. Anabela Pañart
#
#  Estructura de carpetas esperada:
#  ├── app.py
#  ├── requirements.txt
#  ├── templates/
#  │   └── index.html
#  └── static/
#      ├── css/         ← (opcional) CSS externo futuro
#      ├── js/          ← (opcional) JS externo futuro
#      ├── pdfs/        ← Colocá aquí los PDFs reales para descarga
#      └── uploads/     ← Para futuros archivos subidos
#
#  Para correr el servidor:
#  1. Activar entorno virtual: source venv/bin/activate  (Mac/Linux)
#                              venv\Scripts\activate     (Windows)
#  2. Instalar dependencias:   pip install -r requirements.txt
#  3. Correr servidor:         python app.py
#  4. Abrir en browser:        http://127.0.0.1:5000
# ═══════════════════════════════════════════════════════════════════════

from flask import Flask, render_template, send_from_directory, jsonify, request
import os

# ── Inicialización ──────────────────────────────────────────────────────
app = Flask(__name__)

# Carpeta donde se guardarán los PDFs reales para descarga
PDF_FOLDER = os.path.join(app.root_path, 'static', 'pdfs')
os.makedirs(PDF_FOLDER, exist_ok=True)

# Carpeta de uploads futuros
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ── Rutas principales ───────────────────────────────────────────────────

@app.route('/')
def index():
    """
    Ruta principal — sirve la SPA completa.
    Todo el routing de vistas (Dashboard, LMS, Social Hub, Contacto)
    lo maneja JavaScript en el cliente.
    """
    return render_template('index.html')


@app.route('/descargar/<nombre_archivo>')
def descargar_pdf(nombre_archivo):
    """
    Ruta de descarga directa de PDFs.
    Colocá los archivos PDF en la carpeta static/pdfs/
    y actualizá los url_pdf en el DATA del index.html con:
    /descargar/nombre_del_archivo.pdf

    Ejemplo en DATA:
        url_pdf: '/descargar/guia_divorcio.pdf'
    """
    return send_from_directory(
        PDF_FOLDER,
        nombre_archivo,
        as_attachment=True
    )


@app.route('/contacto', methods=['POST'])
def recibir_contacto():
    """
    Endpoint para recibir el formulario de contacto vía AJAX (opcional).
    Por defecto el formulario del index.html usa JS puro con feedback visual.
    Esta ruta está lista para cuando se quiera conectar un backend real
    (envío de emails con Flask-Mail, guardado en base de datos, etc.)

    Ejemplo de payload JSON esperado:
    {
        "nombre": "María García",
        "email": "maria@email.com",
        "telefono": "+54 11 1234-5678",
        "area": "Divorcio / Separación",
        "mensaje": "Necesito orientación sobre..."
    }
    """
    data = request.get_json(silent=True) or request.form.to_dict()

    # ── TODO: Conectar aquí el envío de email con Flask-Mail ──
    # from flask_mail import Mail, Message
    # mail.send_message(...)

    # ── TODO: Conectar aquí guardado en base de datos ──
    # db.session.add(Consulta(**data))
    # db.session.commit()

    # Por ahora, simplemente confirma recepción
    print(f"\n📬 Nueva consulta recibida:")
    print(f"   Nombre:  {data.get('nombre', 'N/A')}")
    print(f"   Email:   {data.get('email', 'N/A')}")
    print(f"   Área:    {data.get('area', 'N/A')}")
    print(f"   Mensaje: {data.get('mensaje', 'N/A')[:60]}...\n")

    return jsonify({
        'status': 'ok',
        'mensaje': 'Consulta recibida. Responderemos en 24-48 hs hábiles.'
    })


@app.route('/api/recursos')
def api_recursos():
    """
    Endpoint de API opcional — devuelve la lista de PDFs disponibles
    en la carpeta static/pdfs/ para sincronizar dinámicamente.
    Útil si en el futuro se sube contenido sin tocar el HTML.
    """
    archivos = []
    if os.path.exists(PDF_FOLDER):
        for f in os.listdir(PDF_FOLDER):
            if f.endswith('.pdf'):
                archivos.append({
                    'nombre': f,
                    'url': f'/descargar/{f}',
                    'tamaño_kb': round(os.path.getsize(os.path.join(PDF_FOLDER, f)) / 1024, 1)
                })
    return jsonify({'total': len(archivos), 'archivos': archivos})


# ── Manejo de errores ───────────────────────────────────────────────────

@app.errorhandler(404)
def pagina_no_encontrada(e):
    """Redirige cualquier ruta desconocida al index (necesario para SPA)."""
    return render_template('index.html'), 200


@app.errorhandler(500)
def error_interno(e):
    return jsonify({'error': 'Error interno del servidor', 'detalle': str(e)}), 500


# ── Punto de entrada ────────────────────────────────────────────────────

if __name__ == '__main__':
    print("\n" + "═" * 55)
    print("  🏛️  Plataforma Jurídica · Dra. Anabela Pañart")
    print("  🌐  Servidor corriendo en: http://127.0.0.1:5000")
    print("  📁  PDFs en:  static/pdfs/")
    print("  ⚙️   Modo:     Desarrollo (debug=True)")
    print("═" * 55 + "\n")

    # debug=True recarga el servidor automáticamente al guardar cambios.
    # Cambiar a debug=False en producción.
    app.run(debug=True, host='127.0.0.1', port=5000)
