import React, { useEffect, useState } from 'react';
import { blogsAPI } from '../../utils/api';
import './Blogs.css';

const Blogs = () => {
  const [blogs, setBlogs] = useState([]);
  const [keyword, setKeyword] = useState('');
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadBlogs();
  }, []);

  const loadBlogs = async () => {
    try {
      setLoading(true);
      const res = await blogsAPI.getAll();
      setBlogs(res.data || res);
    } catch (err) {
      console.error('Error loading blogs', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!title.trim() && !keyword.trim()) {
      loadBlogs();
      return;
    }
    
    try {
      setLoading(true);
      console.log('Searching with params:', { title: title.trim(), keyword: keyword.trim() });
      const res = await blogsAPI.search({ 
        title: title.trim(),
        keyword: keyword.trim()
      });
      console.log('Search response:', res);
      const data = res.data || res;
      console.log('Processed data:', data);
      setBlogs(data);
    } catch (err) {
      console.error('Search error', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="blogs-page">
      <h2>Blogs</h2>

      <form onSubmit={handleSearch} className="blogs-search-form">
        <input
          placeholder="Search by title..."
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="search-input"
        />
        <input
          placeholder="Search by keywords..."
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          className="search-input"
        />
        <button type="submit" className="search-button" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
        <button 
          type="button" 
          className="clear-button"
          onClick={() => { 
            setKeyword(''); 
            setTitle(''); 
            loadBlogs(); 
          }}
          disabled={loading}
        >
          Clear
        </button>
      </form>

      <div className="blogs-list">
        {loading ? (
          <div className="loading">Searching blogs...</div>
        ) : blogs && blogs.length ? (
          blogs.map((blog, idx) => {
            console.log('Rendering blog:', blog);
            return (
              <div key={idx} className="blog-card">
                <h3>{blog.blogTitle || blog.title}</h3>
                <div className="blog-meta">
                  <span className="blog-date">{blog.publicationDate}</span>
                  {blog.category && (
                    <span className="blog-category">{blog.category}</span>
                  )}
                </div>
                <p className="blog-content">{blog.blogContent || blog.content}</p>
              </div>
            );
          })
        ) : (
          <p className="no-results">No blogs found matching your search.</p>
        )}
      </div>
    </div>
  );
};

export default Blogs;
