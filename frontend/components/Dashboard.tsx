import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';

const DashboardContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2rem;
`;

const Section = styled.section`
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
`;

const Title = styled.h2`
  margin-top: 0;
  color: #2c3e50;
`;

const FeatureGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
`;

const FeatureCard = styled.div`
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  }
`;

const FeatureTitle = styled.h3`
  margin: 0 0 0.5rem 0;
  color: #3498db;
`;

const FeatureDescription = styled.p`
  margin: 0.5rem 0;
  color: #7f8c8d;
`;

const ActionButton = styled(Link)`
  display: inline-block;
  background-color: #3498db;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s;

  &:hover {
    background-color: #2980b9;
  }
`;

const Dashboard: React.FC = () => {
  return (
    <DashboardContainer>
      <Section>
        <Title>Welcome to Multi-Modal Content Analytics</Title>
        <p>
          Upload documents, images, audio, and video files to extract intelligence, 
          create embeddings for semantic search, and enable AI-powered chat with 
          agentic multi-step workflows.
        </p>
      </Section>

      <Section>
        <Title>Key Features</Title>
        <FeatureGrid>
          <FeatureCard>
            <FeatureTitle>Document Processing</FeatureTitle>
            <FeatureDescription>
              Extract text and metadata from PDFs, Word docs, and other document formats
            </FeatureDescription>
            <ActionButton to="/upload">Upload Documents</ActionButton>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureTitle>Image Analysis</FeatureTitle>
            <FeatureDescription>
              Analyze images using OCR and computer vision techniques
            </FeatureDescription>
            <ActionButton to="/upload">Upload Images</ActionButton>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureTitle>Audio Transcription</FeatureTitle>
            <FeatureDescription>
              Convert speech to text with high accuracy
            </FeatureDescription>
            <ActionButton to="/upload">Upload Audio</ActionButton>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureTitle>Video Processing</FeatureTitle>
            <FeatureDescription>
              Extract text from video frames and transcribe audio
            </FeatureDescription>
            <ActionButton to="/upload">Upload Video</ActionButton>
          </FeatureCard>
        </FeatureGrid>
      </Section>

      <Section>
        <Title>Get Started</Title>
        <p>
          Begin by <Link to="/upload">uploading your content</Link> or <Link to="/search">searching</Link> through existing content.
          You can also engage in <Link to="/chat">AI-powered conversations</Link> about your content.
        </p>
      </Section>
    </DashboardContainer>
  );
};

export default Dashboard;