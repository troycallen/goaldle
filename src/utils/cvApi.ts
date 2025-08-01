const CV_API_BASE_URL = process.env.NEXT_PUBLIC_CV_API_URL || 'http://localhost:8000';

export interface VideoProcessingResult {
  success: boolean;
  blurred_video?: string; // base64 encoded
  video_info?: {
    fps: number;
    width: number;
    height: number;
    total_frames: number;
    processed_frames: number;
    blur_strength: number;
  };
  processed_at?: string;
  error?: string;
}

export class CVApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = CV_API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('CV API health check failed:', error);
      throw error;
    }
  }

  async processVideo(file: File, blurStrength: number = 50): Promise<VideoProcessingResult> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('blur_strength', blurStrength.toString());

      const response = await fetch(`${this.baseUrl}/process-video`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Video processing failed:', error);
      throw error;
    }
  }

  // Helper method to convert base64 video to blob URL
  static base64ToBlobUrl(base64Data: string, mimeType: string = 'video/mp4'): string {
    const byteCharacters = atob(base64Data);
    const byteNumbers = new Array(byteCharacters.length);
    
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: mimeType });
    return URL.createObjectURL(blob);
  }
}

// Export a default instance
export const cvApiClient = new CVApiClient(); 