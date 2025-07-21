import { NextRequest, NextResponse } from 'next/server';
import { writeFile } from 'fs/promises';
import { join } from 'path';
import { imageAnalyzer, ImageAnalysisResult } from '@/utils/imageAnalysis';

export async function POST(request: NextRequest) {
  try {
    const data = await request.formData();
    const file: File | null = data.get('image') as unknown as File;

    if (!file) {
      return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
      return NextResponse.json({ error: 'Invalid file type' }, { status: 400 });
    }

    // Convert file to buffer
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    // Save file temporarily (in production, you might use cloud storage)
    const filename = `${Date.now()}-${file.name}`;
    const filepath = join(process.cwd(), 'public', 'uploads', filename);
    
    // Ensure uploads directory exists
    try {
      await writeFile(filepath, buffer);
    } catch (error) {
      console.error('Error saving file:', error);
    }

    // Analyze the image
    const imageElement = await imageAnalyzer.preprocessImage(file);
    const analysisResult: ImageAnalysisResult = await imageAnalyzer.analyzeImage(imageElement);

    // Generate hints based on analysis
    const hints = imageAnalyzer.generateHints(analysisResult.playerFeatures);

    return NextResponse.json({
      success: true,
      analysis: analysisResult,
      hints: hints,
      imageUrl: `/uploads/${filename}`
    });

  } catch (error) {
    console.error('Error processing image:', error);
    return NextResponse.json(
      { error: 'Failed to process image' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({ message: 'Image analysis API endpoint' });
}