from flask import Blueprint, request, jsonify
from src.models.news import db, NewsArticle, NewsSource
from src.services.news_fetcher import NewsFetcher
from src.services.news_summarizer import NewsSummarizer
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

news_bp = Blueprint('news', __name__)

# Instanciar servicios
news_fetcher = NewsFetcher()
news_summarizer = NewsSummarizer()

@news_bp.route('/news', methods=['GET'])
def get_news():
    """
    Obtiene las noticias almacenadas con paginación
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Limitar per_page para evitar sobrecarga
        per_page = min(per_page, 50)
        
        # Consultar noticias ordenadas por fecha de publicación
        news_query = NewsArticle.query.order_by(NewsArticle.published_at.desc())
        
        # Paginación
        paginated_news = news_query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        news_list = [article.to_dict() for article in paginated_news.items]
        
        return jsonify({
            'success': True,
            'news': news_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated_news.total,
                'pages': paginated_news.pages,
                'has_next': paginated_news.has_next,
                'has_prev': paginated_news.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Error al obtener noticias: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@news_bp.route('/news/fetch', methods=['POST'])
def fetch_news():
    """
    Captura nuevas noticias de las fuentes configuradas
    """
    try:
        data = request.get_json() or {}
        source_type = data.get('source_type', 'newsapi')
        
        articles = []
        
        if source_type == 'newsapi':
            # Usar una clave de API de ejemplo (en producción debería estar en configuración)
            api_key = data.get('api_key')
            if not api_key:
                return jsonify({
                    'success': False, 
                    'error': 'Se requiere api_key para NewsAPI'
                }), 400
            
            country = data.get('country', 'us')
            category = data.get('category')
            
            articles = news_fetcher.fetch_from_newsapi(
                api_key=api_key,
                country=country,
                category=category
            )
        
        elif source_type == 'rss':
            rss_url = data.get('rss_url')
            if not rss_url:
                return jsonify({
                    'success': False, 
                    'error': 'Se requiere rss_url para RSS'
                }), 400
            
            articles = news_fetcher.fetch_from_rss(rss_url)
        
        elif source_type == 'scraping':
            url = data.get('url')
            title_selector = data.get('title_selector')
            content_selector = data.get('content_selector', '')
            
            if not url or not title_selector:
                return jsonify({
                    'success': False, 
                    'error': 'Se requieren url y title_selector para scraping'
                }), 400
            
            articles = news_fetcher.scrape_website(url, title_selector, content_selector)
        
        else:
            return jsonify({
                'success': False, 
                'error': 'Tipo de fuente no válido'
            }), 400
        
        if not articles:
            return jsonify({
                'success': True, 
                'message': 'No se encontraron nuevas noticias',
                'articles_saved': 0
            })
        
        # Generar resúmenes para los artículos
        articles_with_summaries = news_summarizer.summarize_multiple_articles(articles)
        
        # Guardar artículos en la base de datos
        saved_count = 0
        for article_data in articles_with_summaries:
            try:
                # Verificar si el artículo ya existe (por URL)
                existing_article = NewsArticle.query.filter_by(
                    url=article_data.get('url')
                ).first()
                
                if existing_article:
                    continue  # Saltar artículos duplicados
                
                # Crear nuevo artículo
                article = NewsArticle(
                    title=article_data.get('title', ''),
                    description=article_data.get('description', ''),
                    content=article_data.get('content', ''),
                    url=article_data.get('url', ''),
                    url_to_image=article_data.get('url_to_image', ''),
                    source_name=article_data.get('source_name', ''),
                    author=article_data.get('author', ''),
                    published_at=article_data.get('published_at'),
                    summary=article_data.get('summary'),
                    summary_generated_at=article_data.get('summary_generated_at')
                )
                
                db.session.add(article)
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error al guardar artículo: {str(e)}")
                continue
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Se capturaron y guardaron {saved_count} noticias',
            'articles_saved': saved_count
        })
        
    except Exception as e:
        logger.error(f"Error al capturar noticias: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@news_bp.route('/news/digest', methods=['GET'])
def get_news_digest():
    """
    Genera un digest de las noticias más recientes
    """
    try:
        # Obtener las noticias más recientes (últimas 24 horas)
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        recent_articles = NewsArticle.query.filter(
            NewsArticle.published_at >= yesterday
        ).order_by(NewsArticle.published_at.desc()).limit(10).all()
        
        if not recent_articles:
            # Si no hay noticias recientes, usar las más recientes disponibles
            recent_articles = NewsArticle.query.order_by(
                NewsArticle.published_at.desc()
            ).limit(5).all()
        
        # Convertir a diccionarios
        articles_data = [article.to_dict() for article in recent_articles]
        
        # Generar digest
        digest = news_summarizer.generate_news_digest(articles_data)
        
        return jsonify({
            'success': True,
            'digest': digest,
            'articles_count': len(articles_data),
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error al generar digest: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@news_bp.route('/news/<int:news_id>', methods=['GET'])
def get_news_by_id(news_id):
    """
    Obtiene una noticia específica por ID
    """
    try:
        article = NewsArticle.query.get_or_404(news_id)
        return jsonify({
            'success': True,
            'news': article.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error al obtener noticia {news_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@news_bp.route('/sources', methods=['GET'])
def get_sources():
    """
    Obtiene las fuentes de noticias configuradas
    """
    try:
        sources = NewsSource.query.filter_by(is_active=True).all()
        sources_list = [source.to_dict() for source in sources]
        
        return jsonify({
            'success': True,
            'sources': sources_list
        })
        
    except Exception as e:
        logger.error(f"Error al obtener fuentes: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@news_bp.route('/sources', methods=['POST'])
def add_source():
    """
    Agrega una nueva fuente de noticias
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({
                'success': False, 
                'error': 'Se requiere el nombre de la fuente'
            }), 400
        
        source = NewsSource(
            name=data.get('name'),
            url=data.get('url', ''),
            source_type=data.get('source_type', 'api'),
            api_key=data.get('api_key', ''),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(source)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Fuente agregada exitosamente',
            'source': source.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error al agregar fuente: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

