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
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