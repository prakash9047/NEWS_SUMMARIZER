import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useParams } from 'react-router-dom'
import NewsCard from '../../components/NewsCard'

function CategoryPage() {
  const { category } = useParams()
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchCategoryNews = async () => {
      setLoading(true)
      try {
        const res = await axios.get(`http://127.0.0.1:8000/api/news/?category=${category}`)
        setArticles(res.data)
      } catch (error) {
        console.error(error)
      }
      setLoading(false)
    }
    fetchCategoryNews()
  }, [category])

  return (
    <div>
      <h2>Category: {category}</h2>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="news-grid">
          {articles.map((article) => (
            <NewsCard key={article.id} article={article} />
          ))}
        </div>
      )}
    </div>
  )
}

export default CategoryPage
