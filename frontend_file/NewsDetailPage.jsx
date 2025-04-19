import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useParams } from 'react-router-dom'

function NewsDetailPage() {
  const { id } = useParams()
  const [article, setArticle] = useState(null)
  const [summary, setSummary] = useState('')
  const [translated, setTranslated] = useState('')

  useEffect(() => {
    const fetchArticle = async () => {
      try {
        const res = await axios.get(`http://127.0.0.1:8000/api/news/${id}/`)
        setArticle(res.data)
      } catch (error) {
        console.error(error)
      }
    }
    fetchArticle()
  }, [id])

  const handleSummarize = async () => {
    try {
      const res = await axios.get(`http://127.0.0.1:8000/api/news/summarize/${id}/`)
      setSummary(res.data.summary)
    } catch (error) {
      console.error(error)
    }
  }

  const handleTranslate = async (lang = 'es') => {
    try {
      const res = await axios.get(`http://127.0.0.1:8000/api/news/translate/${id}/?lang=${lang}`)
      setTranslated(res.data.translated)
    } catch (error) {
      console.error(error)
    }
  }

  if (!article) return <p>Loading...</p>

  return (
    <div>
      <h2>{article.title}</h2>
      {article.urlToImage && <img src={article.urlToImage} alt={article.title} style={{ width: '50%' }} />}
      <p><strong>Author:</strong> {article.author}</p>
      <p><strong>Published At:</strong> {article.publishedAt}</p>
      <p>{article.content}</p>

      <button onClick={handleSummarize}>Summarize</button>
      {summary && (
        <div>
          <h3>Summary</h3>
          <p>{summary}</p>
        </div>
      )}

      <button onClick={() => handleTranslate('es')}>Translate to Spanish</button>
      <button onClick={() => handleTranslate('fr')}>Translate to French</button>
      {/* Add more languages if desired */}
      {translated && (
        <div>
          <h3>Translated</h3>
          <p>{translated}</p>
        </div>
      )}
    </div>
  )
}

export default NewsDetailPage
