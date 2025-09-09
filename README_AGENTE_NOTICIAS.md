# Agente de Noticias IA

Un sistema inteligente que captura información de internet y genera resúmenes automáticos de noticias usando IA.

## 🚀 Características

- **Captura múltiple**: NewsAPI, RSS feeds, y web scraping
- **IA integrada**: Resúmenes automáticos con GPT-4.1-mini
- **Interfaz moderna**: Dashboard responsive con estadísticas
- **Base de datos**: Almacenamiento estructurado de noticias
- **API REST**: Endpoints completos para todas las operaciones

## 📋 Requisitos

- Python 3.11+
- pip (gestor de paquetes de Python)
- Clave de API de OpenAI (opcional, usa Manus por defecto)

## 🛠️ Instalación

1. **Extraer el proyecto**
   ```bash
   unzip agente_noticias_ia.zip
   cd news_agent
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   
   # En Windows:
   venv\Scripts\activate
   
   # En macOS/Linux:
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno (opcional)**
   ```bash
   # Para usar OpenAI directamente
   export OPENAI_API_KEY="tu_clave_aqui"
   export OPENAI_API_BASE="https://api.openai.com/v1"
   ```

## 🚀 Uso

1. **Iniciar el servidor**
   ```bash
   python src/main.py
   ```

2. **Abrir en el navegador**
   ```
   http://localhost:5000
   ```

3. **Capturar noticias**
   - Haz clic en "Capturar Noticias"
   - Selecciona el tipo de fuente:
     - **NewsAPI**: Requiere clave de API
     - **RSS Feed**: Ingresa URL del RSS
     - **Web Scraping**: URL + selector CSS

4. **Generar digest**
   - Haz clic en "Generar Digest"
   - Obtén un resumen ejecutivo de las noticias

## 📁 Estructura del Proyecto

```
news_agent/
├── src/
│   ├── main.py              # Punto de entrada
│   ├── models/              # Modelos de base de datos
│   │   ├── user.py
│   │   └── news.py
│   ├── routes/              # Rutas de la API
│   │   ├── user.py
│   │   └── news.py
│   ├── services/            # Lógica de negocio
│   │   ├── news_fetcher.py  # Captura de noticias
│   │   └── news_summarizer.py # Resúmenes con IA
│   ├── static/              # Frontend
│   │   ├── index.html
│   │   └── script.js
│   └── database/
│       └── app.db           # Base de datos SQLite
├── requirements.txt         # Dependencias
└── README.md
```

## 🔧 API Endpoints

### Noticias
- `GET /api/news` - Obtener noticias con paginación
- `POST /api/news/fetch` - Capturar nuevas noticias
- `GET /api/news/digest` - Generar digest de noticias
- `GET /api/news/{id}` - Obtener noticia específica

### Fuentes
- `GET /api/sources` - Obtener fuentes configuradas
- `POST /api/sources` - Agregar nueva fuente

## 🎨 Personalización

### Cambiar el título y branding
Edita `src/static/index.html`:
```html
<h1 class="text-3xl font-bold">Tu Marca Aquí</h1>
```

### Modificar colores
Cambia las clases CSS en `index.html`:
```css
.gradient-bg {
    background: linear-gradient(135deg, #tu-color1 0%, #tu-color2 100%);
}
```

### Usar tu propia API de OpenAI
Modifica `src/services/news_summarizer.py`:
```python
# Cambiar la configuración del cliente OpenAI
self.client = openai.OpenAI(
    api_key="tu_clave_aqui",
    base_url="https://api.openai.com/v1"
)
```

## 🌐 Despliegue en Producción

### Opción 1: Heroku
1. Instalar Heroku CLI
2. Crear `Procfile`:
   ```
   web: python src/main.py
   ```
3. Desplegar:
   ```bash
   heroku create tu-app-noticias
   git push heroku main
   ```

### Opción 2: VPS/Servidor
1. Subir archivos al servidor
2. Instalar dependencias
3. Usar gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
   ```

### Opción 3: Docker
Crear `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "src/main.py"]
```

## 🔒 Seguridad

- Cambia la `SECRET_KEY` en `src/main.py`
- Usa HTTPS en producción
- Configura variables de entorno para claves sensibles
- Implementa autenticación si es necesario

## 🐛 Solución de Problemas

### Error de modelo de IA
Si obtienes errores de modelo no soportado, verifica que uses:
- `gpt-4.1-mini`
- `gpt-4.1-nano`
- `gemini-2.5-flash`

### Error de dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Error de base de datos
Elimina `src/database/app.db` y reinicia la aplicación.

## 📞 Soporte

Para problemas técnicos:
1. Verifica los logs en la consola
2. Revisa la configuración de variables de entorno
3. Asegúrate de que todas las dependencias estén instaladas

## 📄 Licencia

Este proyecto es de tu propiedad completa. Puedes modificarlo, distribuirlo y usarlo comercialmente sin restricciones.

---

**¡Disfruta tu agente de noticias IA!** 🤖📰

