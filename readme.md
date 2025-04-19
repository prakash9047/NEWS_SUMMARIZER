my-news-project/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── README.md
│   ├── crontab
│   ├── config/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── news_app/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── utils/
│   │   │   ├── news_fetcher.py
│   │   │   ├── summarizer.py
│   │   │   └── translator.py
│   │   ├── views.py
│   │   └── services/
│   │       └── recommendation.py
│   └── ...
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx
    │   ├── App.css
    │   ├── components/
    │   │   ├── Header.jsx
    │   │   ├── Footer.jsx
    │   │   ├── NewsCard.jsx
    │   │   ├── SearchBar.jsx
    │   │   └── ...
    │   ├── pages/
    │   │   ├── HomePage.jsx
    │   │   ├── NewsDetailPage.jsx
    │   │   ├── CategoryPage.jsx
    │   │   ├── LoginPage.jsx
    │   │   ├── RegisterPage.jsx
    │   │   └── ...
    │   ├── services/
    │   │   └── api.js
    │   └── ...
    └── ...

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
