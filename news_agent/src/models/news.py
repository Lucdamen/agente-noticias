from src.models.user import db
from datetime import datetime

class NewsArticle(db.Model):
    __tablename__ = 'news_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    url = db.Column(db.String(1000))
    url_to_image = db.Column(db.String(1000))
    source_name = db.Column(db.String(200))
    author = db.Column(db.String(200))
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos para el resumen generado por IA
    summary = db.Column(db.Text)
    summary_generated_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'url': self.url,
            'url_to_image': self.url_to_image,
            'source_name': self.source_name,
            'author': self.author,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'summary': self.summary,
            'summary_generated_at': self.summary_generated_at.isoformat() if self.summary_generated_at else None
        }

class NewsSource(db.Model):
    __tablename__ = 'news_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(1000))
    source_type = db.Column(db.String(50))  # 'api' o 'scraping'
    api_key = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'source_type': self.source_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

