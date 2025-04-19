// Language options for translation
const LANGUAGES = {
    'ar': 'Arabic',
    'bn': 'Bengali',
    'zh': 'Chinese',
    'en': 'English',
    'fr': 'French',
    'de': 'German',
    'hi': 'Hindi',
    'id': 'Indonesian',
    'it': 'Italian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'es': 'Spanish',
    'tr': 'Turkish'
};

// Function to handle text summarization and translation
async function processText(text, maxLength = 150, targetLang = 'hi') {
    try {
        console.log('Processing text with params:', { text, maxLength, targetLang });
        const response = await fetch('http://127.0.0.1:8000/api/summarize/text', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                max_length: maxLength,
                target_lang: targetLang
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('API Error:', errorData);
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('API Response:', data);
        return data;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// Function to create language selector
function createLanguageSelector() {
    const select = document.createElement('select');
    select.className = 'language-selector';
    
    Object.entries(LANGUAGES).forEach(([code, name]) => {
        const option = document.createElement('option');
        option.value = code;
        option.textContent = name;
        select.appendChild(option);
    });
    
    return select;
}

// Function to load news articles
async function loadNews(category = '', userId = null) {
    try {
        let endpoint = category ? 
            `http://127.0.0.1:8000/api/news/category/${category}` : 
            'http://127.0.0.1:8000/api/news/latest';
            
        // If userId is provided, get recommended news
        if (userId) {
            endpoint = `http://127.0.0.1:8000/api/news/recommended/${userId}`;
        }
        
        console.log('Fetching news from:', endpoint);
        
        const response = await fetch(endpoint, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            console.error('API Error:', errorData);
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const articles = await response.json();
        console.log('Received articles:', articles);
        
        const newsContainer = document.getElementById('news-container');
        if (!newsContainer) {
            console.error('News container element not found');
            return;
        }
        
        newsContainer.innerHTML = ''; // Clear existing content

        if (!articles || articles.length === 0) {
            newsContainer.innerHTML = '<div class="error">No news articles found. Please try again later.</div>';
            return;
        }

        articles.forEach(article => {
            const articleElement = createArticleElement(article);
            newsContainer.appendChild(articleElement);
        });

        // Track user interaction with articles
        trackUserInteraction(articles);
    } catch (error) {
        console.error('Error loading news:', error);
        const newsContainer = document.getElementById('news-container');
        if (newsContainer) {
            newsContainer.innerHTML = `
                <div class="error">
                    <p>Failed to load news. Please try again later.</p>
                    <p>Error details: ${error.message}</p>
                </div>
            `;
        }
    }
}

// Function to track user interaction with articles
function trackUserInteraction(articles) {
    articles.forEach(article => {
        const articleElement = document.querySelector(`[data-article-id="${article.id}"]`);
        if (articleElement) {
            // Track article views
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        sendUserInteraction(article.id, 'view');
                    }
                });
            });
            observer.observe(articleElement);

            // Track clicks on "Read More"
            const readMoreLink = articleElement.querySelector('.read-more');
            if (readMoreLink) {
                readMoreLink.addEventListener('click', () => {
                    sendUserInteraction(article.id, 'click');
                });
            }
        }
    });
}

// Function to send user interaction data to backend
async function sendUserInteraction(articleId, interactionType) {
    try {
        await fetch('http://127.0.0.1:8000/api/news/interaction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                article_id: articleId,
                interaction_type: interactionType,
                timestamp: new Date().toISOString()
            })
        });
    } catch (error) {
        console.error('Error tracking user interaction:', error);
    }
}

// Function to play text as speech
async function playTextAsSpeech(text, language, button) {
    try {
        // Save original button text
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';

        console.log('Converting to speech:', { text: text.substring(0, 100) + '...', language });
        
        const response = await fetch('http://127.0.0.1:8000/api/news/text-to-speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                language: language
            })
        });

        if (!response.ok) {
            throw new Error('Failed to generate speech');
        }

        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);

        // Update button to show playing state
        button.innerHTML = '<i class="fas fa-pause"></i> Playing...';

        await audio.play();

        // Add event listeners for audio
        audio.onended = () => {
            button.innerHTML = originalText;
            button.disabled = false;
            URL.revokeObjectURL(audioUrl);
        };

        audio.onerror = () => {
            console.error('Audio playback error');
            button.innerHTML = originalText;
            button.disabled = false;
            URL.revokeObjectURL(audioUrl);
        };

    } catch (error) {
        console.error('Error playing speech:', error);
        alert('Failed to play speech. Please try again.');
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Function to create article element
function createArticleElement(article) {
    const articleDiv = document.createElement('div');
    articleDiv.className = 'article';
    articleDiv.setAttribute('data-article-id', article.id);
    
    // Add image if available
    if (article.image_url) {
        const img = document.createElement('img');
        img.src = article.image_url;
        img.alt = article.title;
        img.onerror = function() {
            this.style.display = 'none';
            // Add a placeholder div when image fails to load
            const placeholder = document.createElement('div');
            placeholder.className = 'image-placeholder';
            placeholder.innerHTML = '<i class="fas fa-image"></i>';
            articleDiv.insertBefore(placeholder, articleDiv.firstChild);
        };
        articleDiv.appendChild(img);
    }

    // Add article content
    const content = document.createElement('div');
    content.className = 'article-content';
    
    const title = document.createElement('h2');
    title.textContent = article.title;
    content.appendChild(title);

    if (article.description) {
        const description = document.createElement('p');
        description.textContent = article.description;
        content.appendChild(description);
    }

    // Add summary if available
    if (article.summary) {
        const summary = document.createElement('div');
        summary.className = 'summary';
        summary.innerHTML = `<strong>Summary:</strong> ${article.summary}`;
        content.appendChild(summary);
    }

    // Add translation if available
    if (article.translated_title || article.translated_description) {
        const translation = document.createElement('div');
        translation.className = 'translation';
        if (article.translated_title) {
            translation.innerHTML += `<strong>Translated Title:</strong> ${article.translated_title}<br>`;
        }
        if (article.translated_description) {
            translation.innerHTML += `<strong>Translated Description:</strong> ${article.translated_description}`;
        }
        content.appendChild(translation);
    }

    // Add metadata
    const meta = document.createElement('div');
    meta.className = 'article-meta';
    meta.innerHTML = `
        <span class="source">${article.source}</span>
        <span class="category">${article.category || 'General'}</span>
        <a href="${article.url}" target="_blank" rel="noopener noreferrer" class="read-more">Read More</a>
    `;
    content.appendChild(meta);

    // Add buttons for summarize and translate
    const actions = document.createElement('div');
    actions.className = 'article-actions';
    
    const summarizeBtn = document.createElement('button');
    summarizeBtn.textContent = 'Summarize';
    summarizeBtn.onclick = async () => {
        try {
            summarizeBtn.disabled = true;
            summarizeBtn.textContent = 'Summarizing...';
            const result = await processText(article.description);
            if (result.summary) {
                const summaryDiv = content.querySelector('.summary') || document.createElement('div');
                summaryDiv.className = 'summary';
                summaryDiv.innerHTML = `<strong>Summary:</strong> ${result.summary}`;
                if (!content.querySelector('.summary')) {
                    content.insertBefore(summaryDiv, meta);
                }
            }
        } catch (error) {
            console.error('Error summarizing:', error);
            alert('Failed to summarize text. Please try again.');
        } finally {
            summarizeBtn.disabled = false;
            summarizeBtn.textContent = 'Summarize';
        }
    };
    actions.appendChild(summarizeBtn);

    // Add language selector and translate button
    const languageSelector = createLanguageSelector();
    actions.appendChild(languageSelector);

    const translateBtn = document.createElement('button');
    translateBtn.textContent = 'Translate';
    translateBtn.onclick = async () => {
        try {
            translateBtn.disabled = true;
            translateBtn.textContent = 'Translating...';
            const targetLang = languageSelector.value;
            console.log('Selected language:', targetLang);
            
            const result = await processText(article.description, 150, targetLang);
            console.log('Translation result:', result);
            
            if (result.translation) {
                const translationDiv = content.querySelector('.translation') || document.createElement('div');
                translationDiv.className = 'translation';
                translationDiv.innerHTML = `
                    <strong>Translation (${LANGUAGES[targetLang]}):</strong>
                    <p>${result.translation}</p>
                `;
                if (!content.querySelector('.translation')) {
                    content.insertBefore(translationDiv, meta);
                }
                
                // Enable the translated speak button
                const translatedSpeakBtn = actions.querySelector('.translated-speak-btn');
                if (translatedSpeakBtn) {
                    translatedSpeakBtn.disabled = false;
                }
            } else {
                console.error('No translation received from API');
                alert('Translation failed. Please try again.');
            }
        } catch (error) {
            console.error('Error translating:', error);
            alert('Failed to translate text. Please try again.');
        } finally {
            translateBtn.disabled = false;
            translateBtn.textContent = 'Translate';
        }
    };
    actions.appendChild(translateBtn);

    // Add text-to-speech buttons
    const originalSpeakBtn = document.createElement('button');
    originalSpeakBtn.className = 'original-speak-btn';
    originalSpeakBtn.innerHTML = '<i class="fas fa-volume-up"></i> Play Original';
    originalSpeakBtn.onclick = () => playTextAsSpeech(article.description, 'en', originalSpeakBtn);
    actions.appendChild(originalSpeakBtn);

    const translatedSpeakBtn = document.createElement('button');
    translatedSpeakBtn.className = 'translated-speak-btn';
    translatedSpeakBtn.innerHTML = '<i class="fas fa-volume-up"></i> Play Translated';
    translatedSpeakBtn.disabled = true; // Initially disabled
    translatedSpeakBtn.onclick = () => {
        const translationDiv = content.querySelector('.translation');
        if (translationDiv) {
            const translatedText = translationDiv.querySelector('p').textContent;
            const targetLang = languageSelector.value;
            playTextAsSpeech(translatedText, targetLang, translatedSpeakBtn);
        } else {
            alert('Please translate the text first.');
        }
    };
    actions.appendChild(translatedSpeakBtn);

    // Enable translated speak button when translation is available
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList' && content.querySelector('.translation')) {
                translatedSpeakBtn.disabled = false;
            }
        });
    });
    observer.observe(content, { childList: true, subtree: true });

    content.appendChild(actions);
    articleDiv.appendChild(content);
    return articleDiv;
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Load recommended news if available, otherwise load latest news
    loadNews();

    // Add event listeners for category buttons
    const categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'];
    categories.forEach(category => {
        const button = document.getElementById(`${category}-btn`);
        if (button) {
            button.addEventListener('click', () => loadNews(category));
        }
    });
}); 