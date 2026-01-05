import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from 'styled-components';

import Header from './components/Header';
import UploadSection from './components/UploadSection';
import SearchSection from './components/SearchSection';
import ChatSection from './components/ChatSection';
import Dashboard from './components/Dashboard';

const AppContainer = styled.div`
  min-height: 100vh;
  background-color: #f5f7fa;
`;

const MainContent = styled.main`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
`;

function App() {
  return (
    <Router>
      <AppContainer>
        <Header />
        <MainContent>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<UploadSection />} />
            <Route path="/search" element={<SearchSection />} />
            <Route path="/chat" element={<ChatSection />} />
          </Routes>
        </MainContent>
      </AppContainer>
    </Router>
  );
}

export default App;