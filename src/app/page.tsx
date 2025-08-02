'use client';

import { useState } from 'react';

export default function GoalDle() {
  const [file, setFile] = useState<File | null>(null);
  const [blurredVideo, setBlurredVideo] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processVideo = async () => {
    if (!file) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:8000/process-video', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      
      if (result.success) {
        // Convert base64 to video URL
        const byteCharacters = atob(result.blurred_video);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: 'video/mp4' });
        const videoUrl = URL.createObjectURL(blob);
        setBlurredVideo(videoUrl);
      } else {
        setError(result.error || 'Processing failed');
      }
    } catch (err) {
      setError('Failed to process video');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8">🎯 GoalDle</h1>
        
        <div className="bg-gray-800 rounded-lg p-6 mb-6">
          <h2 className="text-2xl mb-4">Upload Goal Video</h2>
          
          <input
            type="file"
            accept="video/*"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700"
          />
          
          <button
            onClick={processVideo}
            disabled={!file || loading}
            className="mt-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-6 py-2 rounded-lg font-semibold"
          >
            {loading ? 'Processing...' : 'Blur Players'}
          </button>
          
          {error && (
            <div className="mt-4 p-4 bg-red-600 rounded-lg">
              {error}
            </div>
          )}
        </div>
        
        {blurredVideo && (
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-2xl mb-4">Blurred Video</h2>
            <video
              controls
              className="w-full max-w-2xl mx-auto"
              src={blurredVideo}
            />
          </div>
        )}
      </div>
    </div>
  );
}