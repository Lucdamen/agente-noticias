import openai
import logging
from typing import List, Dict, Optional
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsSummarizer:
    """Servicio para generar resúmenes de noticias usando IA"""
    
    def __init__(self):
        # La clave de API ya está configurada en las variables de entorno
        self.client = openai.OpenAI()
    
    def summarize_article(self, article: Dict) -> Optional[str]:
        """
        Genera un resumen de un artículo individual
        """
        try:
            # Preparar el texto del artículo
            text_to_summarize = self._prepare_article_text(article)
            
            if not text_to_summarize or len(text_to_summarize.strip()) < 50:
                logger.warning(f"Texto insuficiente para resumir: {article.get('title', 'Sin título')}")
                return None
            
            # Crear el prompt para el resumen
            prompt = f"""
            Por favor, resume el siguiente artículo de noticias en español de manera concisa y objetiva. 
            El resumen debe:
            - Ser de 2-3 oraciones máximo
            - Capturar los puntos principales
            - Mantener un tono neutral y periodístico
            - Estar en español
            
            Artículo:
            Título: {article.get('title', '')}
            Contenido: {text_to_summarize}
            
            Resumen:
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Eres un periodista experto que crea resúmenes concisos y objetivos de noticias en español."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Limpiar el resumen
            summary = self._clean_summary(summary)
            
            logger.info(f"Resumen generado para: {article.get('title', 'Sin título')[:50]}...")
            return summary
            
        except Exception as e:
            logger.error(f"Error al generar resumen: {str(e)}")
            return None
    
    def summarize_multiple_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Genera resúmenes para múltiples artículos
        """
        summarized_articles = []
        
        for article in articles:
            try:
                summary = self.summarize_article(article)
                
                # Agregar el resumen al artículo
                article_with_summary = article.copy()
                article_with_summary['summary'] = summary
                article_with_summary['summary_generated_at'] = datetime.utcnow()
                
                summarized_articles.append(article_with_summary)
                
                # Pequeña pausa para evitar límites de rate
                import time
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error al procesar artículo {article.get('title', 'Sin título')}: {str(e)}")
                # Agregar el artículo sin resumen
                summarized_articles.append(article)
        
        logger.info(f"Procesados {len(summarized_articles)} artículos")
        return summarized_articles
    
    def generate_news_digest(self, articles: List[Dict], max_articles: int = 5) -> str:
        """
        Genera un digest de noticias combinando múltiples artículos
        """
        try:
            if not articles:
                return "No hay noticias disponibles en este momento."
            
            # Seleccionar los artículos más recientes
            sorted_articles = sorted(
                articles, 
                key=lambda x: x.get('published_at', datetime.min), 
                reverse=True
            )[:max_articles]
            
            # Preparar el contenido para el digest
            articles_text = ""
            for i, article in enumerate(sorted_articles, 1):
                title = article.get('title', 'Sin título')
                summary = article.get('summary', article.get('description', ''))
                source = article.get('source_name', 'Fuente desconocida')
                
                articles_text += f"{i}. {title}\n"
                articles_text += f"   Fuente: {source}\n"
                articles_text += f"   {summary}\n\n"
            
            # Crear el prompt para el digest
            prompt = f"""
            Crea un digest de noticias en español basado en los siguientes artículos. 
            El digest debe:
            - Ser un resumen ejecutivo de las noticias más importantes
            - Estar bien estructurado y ser fácil de leer
            - Mantener un tono profesional y periodístico
            - Incluir los puntos más relevantes de cada noticia
            - Tener entre 200-300 palabras
            
            Noticias:
            {articles_text}
            
            Digest de Noticias:
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Eres un editor de noticias experto que crea digests informativos y bien estructurados en español."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.4
            )
            
            digest = response.choices[0].message.content.strip()
            
            logger.info("Digest de noticias generado exitosamente")
            return digest
            
        except Exception as e:
            logger.error(f"Error al generar digest: {str(e)}")
            return "Error al generar el digest de noticias."
    
    def _prepare_article_text(self, article: Dict) -> str:
        """
        Prepara el texto del artículo para el resumen
        """
        text_parts = []
        
        # Agregar título
        if article.get('title'):
            text_parts.append(article['title'])
        
        # Agregar descripción
        if article.get('description'):
            text_parts.append(article['description'])
        
        # Agregar contenido (limitado)
        if article.get('content'):
            content = article['content']
            # Limitar el contenido a 1000 caracteres para evitar tokens excesivos
            if len(content) > 1000:
                content = content[:1000] + "..."
            text_parts.append(content)
        
        return " ".join(text_parts)
    
    def _clean_summary(self, summary: str) -> str:
        """
        Limpia y formatea el resumen generado
        """
        # Remover prefijos comunes
        prefixes_to_remove = [
            "Resumen:",
            "El resumen es:",
            "En resumen:",
            "Summary:",
        ]
        
        for prefix in prefixes_to_remove:
            if summary.startswith(prefix):
                summary = summary[len(prefix):].strip()
        
        # Limpiar espacios extra y saltos de línea
        summary = re.sub(r'\s+', ' ', summary).strip()
        
        # Asegurar que termine con punto
        if summary and not summary.endswith('.'):
            summary += '.'
        
        return summary

