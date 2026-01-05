import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const ImageAnalysisContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
`;

const UploadSection = styled.div`
  background: white;
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  margin-bottom: 2rem;
`;

const ResultSection = styled.div`
  background: white;
  border-radius: 8px;
  padding: 2rem;
  margin-top: 2rem;
  min-height: 200px;
`;

const ImagePreview = styled.img`
  max-width: 100%;
  max-height: 300px;
  margin: 1rem 0;
  border-radius: 8px;
`;

const Button = styled.button`
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  margin: 0.5rem;
  font-size: 1rem;

  &:hover {
    background-color: #2980b9;
  }

  &:disabled {
    background-color: #bdc3c7;
    cursor: not-allowed;
  }
`;

const Input = styled.input`
  padding: 0.5rem;
  margin: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 70%;
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-height: 100px;
  margin: 1rem 0;
`;

const ImageAnalysis: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [caption, setCaption] = useState<string>('');
  const [question, setQuestion] = useState<string>('');
  const [answer, setAnswer] = useState<string>('');
  const [imageDescription, setImageDescription] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>('caption'); // 'caption', 'question', 'describe'
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type.startsWith('image/')) {
        setSelectedFile(file);
        setPreviewUrl(URL.createObjectURL(file));
        // Reset results when new image is selected
        setCaption('');
        setAnswer('');
        setImageDescription('');
      } else {
        alert('Please select an image file');
      }
    }
  };

  const handleUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const generateCaption = async () => {
    if (!selectedFile) {
      alert('Please select an image first');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post('http://localhost:8000/api/v1/blip2/image/caption', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setCaption(response.data.caption);
    } catch (error) {
      console.error('Error generating caption:', error);
      setCaption('Error generating caption: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const answerImageQuestion = async () => {
    if (!selectedFile) {
      alert('Please select an image first');
      return;
    }

    if (!question.trim()) {
      alert('Please enter a question');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('question', question);

      const response = await axios.post('http://localhost:8000/api/v1/blip2/image/question', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setAnswer(response.data.answer);
    } catch (error) {
      console.error('Error answering question:', error);
      setAnswer('Error answering question: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const describeImage = async () => {
    if (!selectedFile) {
      alert('Please select an image first');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post('http://localhost:8000/api/v1/blip2/image/describe', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setImageDescription(response.data.description);
    } catch (error) {
      console.error('Error describing image:', error);
      setImageDescription('Error describing image: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ImageAnalysisContainer>
      <h1>BLIP-2 Vision-Language Analysis</h1>
      <p>Upload an image to analyze with the BLIP-2 vision-language model</p>
      
      <UploadSection>
        <h2>Upload Image</h2>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/*"
          style={{ display: 'none' }}
        />
        <Button onClick={handleUploadClick}>
          {selectedFile ? 'Change Image' : 'Select Image'}
        </Button>
        
        {selectedFile && (
          <div>
            <p>Selected: {selectedFile.name}</p>
            {previewUrl && <ImagePreview src={previewUrl} alt="Preview" />}
          </div>
        )}
      </UploadSection>

      <div>
        <Button 
          onClick={() => setActiveTab('caption')} 
          style={{ backgroundColor: activeTab === 'caption' ? '#2980b9' : '#3498db' }}
        >
          Generate Caption
        </Button>
        <Button 
          onClick={() => setActiveTab('question')} 
          style={{ backgroundColor: activeTab === 'question' ? '#2980b9' : '#3498db' }}
        >
          Ask Question
        </Button>
        <Button 
          onClick={() => setActiveTab('describe')} 
          style={{ backgroundColor: activeTab === 'describe' ? '#2980b9' : '#3498db' }}
        >
          Detailed Description
        </Button>
      </div>

      {activeTab === 'caption' && (
        <div>
          <Button onClick={generateCaption} disabled={loading || !selectedFile}>
            {loading ? 'Generating...' : 'Generate Caption'}
          </Button>
          {caption && (
            <ResultSection>
              <h3>Caption:</h3>
              <p>{caption}</p>
            </ResultSection>
          )}
        </div>
      )}

      {activeTab === 'question' && (
        <div>
          <Input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Enter your question about the image..."
          />
          <Button onClick={answerImageQuestion} disabled={loading || !selectedFile || !question.trim()}>
            {loading ? 'Answering...' : 'Answer Question'}
          </Button>
          {answer && (
            <ResultSection>
              <h3>Answer:</h3>
              <p>{answer}</p>
            </ResultSection>
          )}
        </div>
      )}

      {activeTab === 'describe' && (
        <div>
          <Button onClick={describeImage} disabled={loading || !selectedFile}>
            {loading ? 'Describing...' : 'Generate Description'}
          </Button>
          {imageDescription && (
            <ResultSection>
              <h3>Detailed Description:</h3>
              <p>{imageDescription}</p>
            </ResultSection>
          )}
        </div>
      )}
    </ImageAnalysisContainer>
  );
};

export default ImageAnalysis;