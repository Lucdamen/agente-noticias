import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from typing import List, Dict, Optional
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsFetcher:
    """Servicio para capturar noticias de diferentes fuentes"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_from_newsapi(self, api_key: str, country: str = 'us', category: str = None, page_size: int = 20) -> List[Dict]:
        """
        Captura noticias desde NewsAPI
        """
        try:
            url = 'https://newsapi.org/v2/top-headlines'
            params = {
                'apiKey': api_key,
                'country': country,
                'pageSize': page_size
            }
            
            if category:
                params['category'] = category
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'ok':
                articles = []
                for article in data['articles']:
                    processed_article = {
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'content': article.get('content', ''),
                        'url': article.get('url', ''),
                        'url_to_image': article.get('urlToImage', ''),
                        'source_name': article.get('source', {}).get('name', ''),
                        'author': article.get('author', ''),
                        'published_at': self._parse_datetime(article.get('publishedAt'))
                    }
                    articles.append(processed_article)
                
                logger.info(f"Capturadas {len(articles)} noticias desde NewsAPI")
                return articles
            else:
                logger.error(f"Error en NewsAPI: {data.get('message', 'Error desconocido')}")
                return []
                
        except Exception as e:
            logger.error(f"Error al capturar desde NewsAPI: {str(e)}")
            return []
    
    def fetch_from_rss(self, rss_url: str) -> List[Dict]:
        """
        Captura noticias desde un feed RSS
        """
        try:
            import feedparser
            
            feed = feedparser.parse(rss_url)
            articles = []
            
            for entry in feed.entries:
                article = {
                    'title': entry.get('title', ''),
                    'description': entry.get('summary', ''),
                    'content': entry.get('content', [{}])[0].get('value', '') if entry.get('content') else '',
                    'url': entry.get('link', ''),
                    'url_to_image': '',
                    'source_name': feed.feed.get('title', ''),
                    'author': entry.get('author', ''),
                    'published_at': self._parse_datetime(entry.get('published'))
                }
                articles.append(article)
            
            logger.info(f"Capturadas {len(articles)} noticias desde RSS: {rss_url}")
            return articles
            
        except Exception as e:
            logger.error(f"Error al capturar desde RSS {rss_url}: {str(e)}")
            return []
    
    def scrape_website(self, url: str, title_selector: str, content_selector: str) -> List[Dict]:
        """
        Realiza web scraping de un sitio web específico
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Buscar artículos usando los selectores proporcionados
            title_elements = soup.select(title_selector)
            
            for title_elem in title_elements[:10]:  # Limitar a 10 artículos
                article = {
                    'title': title_elem.get_text(strip=True),
                    'description': '',
                    'content': '',
                    'url': self._get_absolute_url(url, title_elem.get('href', '')),
                    'url_to_image': '',
                    'source_name': self._get_domain_name(url),
                    'author': '',
                    'published_at': datetime.utcnow()
                }
                
                # Intentar obtener más contenido si hay un selector de contenido
                if content_selector:
                    content_elem = title_elem.find_next(content_selector)
                    if content_elem:
                        article['description'] = content_elem.get_text(strip=True)[:500]
                
                articles.append(article)
            
            logger.info(f"Scrapeadas {len(articles)} noticias desde {url}")
            return articles
            
        except Exception as e:
            logger.error(f"Error al scrapear {url}: {str(e)}")
            return []
    
    def _parse_datetime(self, date_str: str) -> Optional[datetime]:
        """Convierte string de fecha a datetime"""
        if not date_str:
            return None
        
        try:
            # Formato ISO 8601 (NewsAPI)
            if 'T' in date_str and 'Z' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            # Otros formatos comunes
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y %H:%M:%S',
                '%d/%m/%Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            return datetime.utcnow()
            
        except Exception:
            return datetime.utcnow()
    
    def _get_absolute_url(self, base_url: str, relative_url: str) -> str:
        """Convierte URL relativa a absoluta"""
        if not relative_url:
            return ''
        
        if relative_url.startswith('http'):
            return relative_url
        
        from urllib.parse import urljoin
        return urljoin(base_url, relative_url)
    
    def _get_domain_name(self, url: str) -> str:
        """Extrae el nombre del dominio de una URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except:
            return 'Unknown'

