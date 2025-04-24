# News Summarizer with AI Features

A modern news summarizer application that provides real-time news articles with AI-powered features including summarization, translation, and text-to-speech capabilities.

## Features

- 📰 Real-time news articles from various categories
- 🤖 AI-powered text summarization
- 🌐 Multi-language translation support
- 🔊 Text-to-speech functionality
- 🎯 Personalized news recommendations
- 📱 Responsive design for all devices

- ![image](https://github.com/user-attachments/assets/30605a52-cb91-454d-8c17-0890eb6700ad)


## Tech Stack

### Frontend
- HTML5, CSS3, JavaScript
- Modern UI with responsive design
- Interactive user interface

### Backend
- Python with FastAPI
- SQLAlchemy for database management
- News API for news aggregation
- Groq API for AI features (summarization and translation)
- gTTS for text-to-speech functionality

## Prerequisites

- Python 3.8+
- Node.js (for development)
- News API key
- Groq API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/news-summarizer.git
cd news-summarizer
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```env
NEWS_API_KEY=your_news_api_key
GROQ_API_KEY=your_groq_api_key
```

5. Initialize the database:
```bash
python backend/init_db.py
```

## Running the Application

1. Start the backend server:
```bash
uvicorn backend.main:app --reload
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

## API Endpoints

- `GET /api/news/latest` - Get latest news articles
- `GET /api/news/category/{category}` - Get news by category
- `GET /api/news/recommended/{user_id}` - Get personalized news recommendations
- `POST /api/news/interaction` - Record user interactions
- `POST /api/summarize/text` - Summarize text
- `POST /api/news/text-to-speech` - Convert text to speech

## Project Structure

```
news-aggregator/
├── backend/
│   ├── main.py
│   ├── routes/
│   │   ├── news.py
│   │   └── summarization.py
│   ├── models.py
│   ├── schemas.py
│   └── database.py
├── frontend_file/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── index.html
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


add below to .env


///NEWS_API_KEY=0b5f071b215c40ea89ad29de35a48604
GROQ_API_KEY=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
# JWT Settings
SECRET_KEY=Mlhld8E3RnHMx8YwCxCF6gTBYWYtLw8nRv2wrN2vgNz-kQOcs-2OaeigBwWrURui2Mk2cspnEzoUk9rchtd-aQ
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Settings
DATABASE_URL=sqlite:///./sql_app.db




# 7bfd907035594a30b6f8eab35ad4c68d
