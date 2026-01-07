import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import styled from 'styled-components';
import axios from 'axios';

const UploadContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
`;

const UploadArea = styled.div<{ isDragActive: boolean }>`
  border: 2px dashed ${props => props.isDragActive ? '#3498db' : '#bdc3c7'};
  border-radius: 8px;
  padding: 3rem 2rem;
  text-align: center;
  background-color: ${props => props.isDragActive ? '#f8fafc' : '#f8f9fa'};
  transition: all 0.2s;
  cursor: pointer;

  &:hover {
    border-color: #3498db;
  }
`;

const UploadIcon = styled.div`
  font-size: 3rem;
  color: #bdc3c7;
  margin-bottom: 1rem;
`;

const UploadText = styled.p`
  margin: 0.5rem 0;
  color: #7f8c8d;
`;

const SupportedFormats = styled.p`
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #95a5a6;
`;

const FileList = styled.div`
  margin-top: 2rem;
`;

const FileItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  background-color: white;
`;

const FileName = styled.span`
  font-weight: 500;
  color: #2c3e50;
`;

const FileStatus = styled.span<{ status: string }>`
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  background-color: ${props => {
    if (props.status === 'completed') return '#d4edda';
    if (props.status === 'processing') return '#fff3cd';
    if (props.status === 'failed') return '#f8d7da';
    return '#e2e3e5';
  }};
  color: ${props => {
    if (props.status === 'completed') return '#155724';
    if (props.status === 'processing') return '#856404';
    if (props.status === 'failed') return '#721c24';
    return '#6c757d';
  }};
`;

const UploadSection: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploadStatus, setUploadStatus] = useState<Record<string, string>>({});
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});

  const onDrop = (acceptedFiles: File[]) => {
    setFiles(prev => [...prev, ...acceptedFiles]);
    
    // Process each file
    acceptedFiles.forEach(file => {
      setUploadStatus(prev => ({ ...prev, [file.name]: 'pending' }));
      uploadFile(file);
    });
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
      'audio/*': ['.mp3', '.wav', '.flac', '.aac'],
      'video/*': ['.mp4', '.avi', '.mov', '.mkv']
    }
  });

  const uploadFile = async (file: File) => {
    setUploadStatus(prev => ({ ...prev, [file.name]: 'processing' }));
    setUploadProgress(prev => ({ ...prev, [file.name]: 0 }));

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/v1/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(prev => ({ ...prev, [file.name]: progress }));
          }
        }
      });

      setUploadStatus(prev => ({ ...prev, [file.name]: 'completed' }));
      console.log('Upload response:', response.data);
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus(prev => ({ ...prev, [file.name]: 'failed' }));
    }
  };

  return (
    <UploadContainer>
      <h1>Upload Content</h1>
      <p>Upload documents, images, audio, or video files for AI-powered analysis.</p>
      
      <UploadArea {...getRootProps()} isDragActive={isDragActive}>
        <input {...getInputProps()} />
        <UploadIcon>📁</UploadIcon>
        <UploadText>
          {isDragActive 
            ? "Drop files here..." 
            : "Drag 'n' drop files here, or click to select files"}
        </UploadText>
        <SupportedFormats>
          Supports: PDF, DOC, DOCX, TXT, JPG, PNG, MP3, WAV, MP4, MOV and more
        </SupportedFormats>
      </UploadArea>

      {files.length > 0 && (
        <FileList>
          <h2>Upload Queue</h2>
          {files.map((file, index) => (
            <FileItem key={index}>
              <FileName>{file.name}</FileName>
              <div>
                <FileStatus status={uploadStatus[file.name] || 'pending'}>
                  {uploadStatus[file.name] || 'Pending'}
                </FileStatus>
                {uploadProgress[file.name] !== undefined && uploadProgress[file.name] < 100 && (
                  <span style={{ marginLeft: '10px' }}>
                    {uploadProgress[file.name]}%
                  </span>
                )}
              </div>
            </FileItem>
          ))}
        </FileList>
      )}
    </UploadContainer>
  );
};

export default UploadSection;