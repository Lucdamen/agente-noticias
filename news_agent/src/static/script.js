// Estado global de la aplicación
let currentPage = 1;
let totalPages = 1;
let newsData = [];

// URLs de la API
const API_BASE = '/api';

// Elementos del DOM
const elements = {
    fetchNewsBtn: document.getElementById('fetchNewsBtn'),
    generateDigestBtn: document.getElementById('generateDigestBtn'),
    fetchModal: document.getElementById('fetchModal'),
    fetchForm: document.getElementById('fetchForm'),
    cancelFetch: document.getElementById('cancelFetch'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    sourceType: document.getElementById('sourceType'),
    newsApiFields: document.getElementById('newsApiFields'),
    rssFields: document.getElementById('rssFields'),
    scrapingFields: document.getElementById('scrapingFields'),
    newsGrid: document.getElementById('newsGrid'),
    pagination: document.getElementById('pagination'),
    prevPage: document.getElementById('prevPage'),
    nextPage: document.getElementById('nextPage'),
    pageInfo: document.getElementById('pageInfo'),
    totalNews: document.getElementById('totalNews'),
    lastUpdate: document.getElementById('lastUpdate'),
    summariesCount: document.getElementById('summariesCount'),
    digestSection: document.getElementById('digestSection'),
    digestContent: document.getElementById('digestContent'),
    digestDate: document.getElementById('digestDate')
};

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadNews();
    updateStats();
});

// Event Listeners
function initializeEventListeners() {
    elements.fetchNewsBtn.addEventListener('click', showFetchModal);
    elements.generateDigestBtn.addEventListener('click', generateDigest);
    elements.cancelFetch.addEventListener('click', hideFetchModal);
    elements.fetchForm.addEventListener('submit', handleFetchSubmit);
    elements.sourceType.addEventListener('change', handleSourceTypeChange);
    elements.prevPage.addEventListener('click', () => changePage(currentPage - 1));
    elements.nextPage.addEventListener('click', () => changePage(currentPage + 1));
    
    // Cerrar modal al hacer clic fuera
    elements.fetchModal.addEventListener('click', function(e) {
        if (e.target === elements.fetchModal) {
            hideFetchModal();
        }
    });
}

// Mostrar/ocultar modal de captura
function showFetchModal() {
    elements.fetchModal.classList.remove('hidden');
    handleSourceTypeChange(); // Mostrar campos apropiados
}

function hideFetchModal() {
    elements.fetchModal.classList.add('hidden');
    elements.fetchForm.reset();
}

// Manejar cambio de tipo de fuente
function handleSourceTypeChange() {
    const sourceType = elements.sourceType.value;
    
    // Ocultar todos los campos
    elements.newsApiFields.classList.add('hidden');
    elements.rssFields.classList.add('hidden');
    elements.scrapingFields.classList.add('hidden');
    
    // Mostrar campos apropiados
    switch(sourceType) {
        case 'newsapi':
            elements.newsApiFields.classList.remove('hidden');
            break;
        case 'rss':
            elements.rssFields.classList.remove('hidden');
            break;
        case 'scraping':
            elements.scrapingFields.classList.remove('hidden');
            break;
    }
}

// Manejar envío del formulario de captura
async function handleFetchSubmit(e) {
    e.preventDefault();
    
    const sourceType = elements.sourceType.value;
    let requestData = { source_type: sourceType };
    
    // Preparar datos según el tipo de fuente
    switch(sourceType) {
        case 'newsapi':
            const apiKey = document.getElementById('apiKey').value;
            const country = document.getElementById('country').value;
            
            if (!apiKey.trim()) {
                showNotification('Por favor, ingresa tu clave de API de NewsAPI', 'error');
                return;
            }
            
            requestData.api_key = apiKey;
            requestData.country = country;
            break;
            
        case 'rss':
            const rssUrl = document.getElementById('rssUrl').value;
            
            if (!rssUrl.trim()) {
                showNotification('Por favor, ingresa la URL del RSS', 'error');
                return;
            }
            
            requestData.rss_url = rssUrl;
            break;
            
        case 'scraping':
            const siteUrl = document.getElementById('siteUrl').value;
            const titleSelector = document.getElementById('titleSelector').value;
            
            if (!siteUrl.trim() || !titleSelector.trim()) {
                showNotification('Por favor, completa todos los campos para web scraping', 'error');
                return;
            }
            
            requestData.url = siteUrl;
            requestData.title_selector = titleSelector;
            break;
    }
    
    // Realizar la petición
    try {
        showLoading(true);
        hideFetchModal();
        
        const response = await fetch(`${API_BASE}/news/fetch`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`Se capturaron ${result.articles_saved} noticias exitosamente`, 'success');
            loadNews(); // Recargar noticias
            updateStats(); // Actualizar estadísticas
        } else {
            showNotification(`Error: ${result.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Error al capturar noticias:', error);
        showNotification('Error al capturar noticias. Inténtalo de nuevo.', 'error');
    } finally {
        showLoading(false);
    }
}

// Cargar noticias
async function loadNews(page = 1) {
    try {
        const response = await fetch(`${API_BASE}/news?page=${page}&per_page=9`);
        const result = await response.json();
        
        if (result.success) {
            newsData = result.news;
            currentPage = result.pagination.page;
            totalPages = result.pagination.pages;
            
            renderNews(newsData);
            updatePagination();
        } else {
            showNotification('Error al cargar noticias', 'error');
        }
        
    } catch (error) {
        console.error('Error al cargar noticias:', error);
        showNotification('Error al cargar noticias', 'error');
    }
}

// Renderizar noticias
function renderNews(news) {
    elements.newsGrid.innerHTML = '';
    
    if (news.length === 0) {
        elements.newsGrid.innerHTML = `
            <div class="col-span-full text-center py-12">
                <i class="fas fa-newspaper text-6xl text-gray-300 mb-4"></i>
                <h3 class="text-xl font-semibold text-gray-600 mb-2">No hay noticias disponibles</h3>
                <p class="text-gray-500">Captura algunas noticias para comenzar</p>
            </div>
        `;
        return;
    }
    
    news.forEach(article => {
        const newsCard = createNewsCard(article);
        elements.newsGrid.appendChild(newsCard);
    });
}

// Crear tarjeta de noticia
function createNewsCard(article) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-lg shadow-md overflow-hidden card-hover fade-in';
    
    const publishedDate = article.published_at ? 
        new Date(article.published_at).toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }) : 'Fecha desconocida';
    
    const imageUrl = article.url_to_image || 'https://via.placeholder.com/400x200?text=Sin+Imagen';
    const summary = article.summary || article.description || 'Sin resumen disponible';
    const title = article.title || 'Sin título';
    const source = article.source_name || 'Fuente desconocida';
    
    card.innerHTML = `
        <div class="relative">
            <img src="${imageUrl}" alt="${title}" class="w-full h-48 object-cover" 
                 onerror="this.src='https://via.placeholder.com/400x200?text=Sin+Imagen'">
            <div class="absolute top-2 right-2">
                <span class="bg-purple-600 text-white px-2 py-1 rounded-full text-xs font-semibold">
                    ${source}
                </span>
            </div>
        </div>
        <div class="p-4">
            <h3 class="font-bold text-lg text-gray-800 mb-2 line-clamp-2">${title}</h3>
            <p class="text-gray-600 text-sm mb-3 line-clamp-3">${summary}</p>
            <div class="flex items-center justify-between text-xs text-gray-500">
                <span><i class="fas fa-calendar-alt mr-1"></i>${publishedDate}</span>
                ${article.summary ? '<span class="text-purple-600"><i class="fas fa-brain mr-1"></i>IA</span>' : ''}
            </div>
            ${article.url ? `
                <div class="mt-3">
                    <a href="${article.url}" target="_blank" 
                       class="inline-flex items-center text-purple-600 hover:text-purple-800 text-sm font-medium">
                        Leer más <i class="fas fa-external-link-alt ml-1"></i>
                    </a>
                </div>
            ` : ''}
        </div>
    `;
    
    return card;
}

// Actualizar paginación
function updatePagination() {
    if (totalPages <= 1) {
        elements.pagination.classList.add('hidden');
        return;
    }
    
    elements.pagination.classList.remove('hidden');
    elements.pageInfo.textContent = `Página ${currentPage} de ${totalPages}`;
    
    elements.prevPage.disabled = currentPage <= 1;
    elements.nextPage.disabled = currentPage >= totalPages;
    
    elements.prevPage.classList.toggle('opacity-50', currentPage <= 1);
    elements.nextPage.classList.toggle('opacity-50', currentPage >= totalPages);
}

// Cambiar página
function changePage(page) {
    if (page >= 1 && page <= totalPages && page !== currentPage) {
        loadNews(page);
    }
}

// Actualizar estadísticas
async function updateStats() {
    try {
        const response = await fetch(`${API_BASE}/news?page=1&per_page=1`);
        const result = await response.json();
        
        if (result.success) {
            const total = result.pagination.total;
            elements.totalNews.textContent = total;
            
            // Contar resúmenes
            const summariesResponse = await fetch(`${API_BASE}/news?page=1&per_page=50`);
            const summariesResult = await summariesResponse.json();
            
            if (summariesResult.success) {
                const summariesCount = summariesResult.news.filter(article => article.summary).length;
                elements.summariesCount.textContent = summariesCount;
            }
            
            // Actualizar fecha de última actualización
            elements.lastUpdate.textContent = new Date().toLocaleString('es-ES');
        }
        
    } catch (error) {
        console.error('Error al actualizar estadísticas:', error);
    }
}

// Generar digest
async function generateDigest() {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/news/digest`);
        const result = await response.json();
        
        if (result.success) {
            elements.digestContent.innerHTML = result.digest.replace(/\n/g, '<br>');
            elements.digestDate.textContent = new Date(result.generated_at).toLocaleString('es-ES');
            elements.digestSection.classList.remove('hidden');
            
            // Scroll al digest
            elements.digestSection.scrollIntoView({ behavior: 'smooth' });
            
            showNotification('Digest generado exitosamente', 'success');
        } else {
            showNotification(`Error al generar digest: ${result.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Error al generar digest:', error);
        showNotification('Error al generar digest', 'error');
    } finally {
        showLoading(false);
    }
}

// Mostrar/ocultar loading
function showLoading(show) {
    if (show) {
        elements.loadingOverlay.classList.remove('hidden');
    } else {
        elements.loadingOverlay.classList.add('hidden');
    }
}

// Mostrar notificaciones
function showNotification(message, type = 'info') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transform transition-all duration-300 translate-x-full`;
    
    // Estilos según el tipo
    switch(type) {
        case 'success':
            notification.classList.add('bg-green-500', 'text-white');
            break;
        case 'error':
            notification.classList.add('bg-red-500', 'text-white');
            break;
        default:
            notification.classList.add('bg-blue-500', 'text-white');
    }
    
    notification.innerHTML = `
        <div class="flex items-center">
            <span class="flex-1">${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-white hover:text-gray-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }, 5000);
}

// Estilos CSS adicionales para line-clamp
const style = document.createElement('style');
style.textContent = `
    .line-clamp-2 {
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .line-clamp-3 {
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
`;
document.head.appendChild(style);

