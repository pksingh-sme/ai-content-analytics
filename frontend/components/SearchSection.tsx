import React, { useState } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const SearchContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
`;

const SearchForm = styled.form`
  display: flex;
  margin-bottom: 2rem;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  font-size: 1rem;
`;

const SearchButton = styled.button`
  padding: 1rem 1.5rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 1rem;

  &:hover {
    background-color: #2980b9;
  }
`;

const ResultsContainer = styled.div`
  margin-top: 2rem;
`;

const ResultItem = styled.div`
  padding: 1.5rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 1rem;
  background-color: white;
`;

const ResultTitle = styled.h3`
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
`;

const ResultContent = styled.p`
  margin: 0.5rem 0;
  color: #34495e;
  line-height: 1.6;
`;

const ResultSource = styled.div`
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #7f8c8d;
`;

const SearchSection: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/v1/query', {
        query: query,
        top_k: 5,
        include_sources: true
      });
      
      setResults(response.data.sources || []);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SearchContainer>
      <h1>Semantic Search</h1>
      <p>Search across all your uploaded content using natural language.</p>
      
      <SearchForm onSubmit={handleSearch}>
        <SearchInput
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your search query..."
          disabled={loading}
        />
        <SearchButton type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </SearchButton>
      </SearchForm>

      {results.length > 0 && (
        <ResultsContainer>
          <h2>Search Results</h2>
          {results.map((result, index) => (
            <ResultItem key={index}>
              <ResultTitle>Result {index + 1}</ResultTitle>
              <ResultContent>{result.content}</ResultContent>
              <ResultSource>
                Source: {result.source?.file_id || 'Unknown'} | 
                Score: {(result.score * 100).toFixed(2)}%
              </ResultSource>
            </ResultItem>
          ))}
        </ResultsContainer>
      )}
    </SearchContainer>
  );
};

export default SearchSection;