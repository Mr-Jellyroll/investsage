
import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(req: NextRequest) {
  try {
    const data = await req.json();
    
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn('python', [
        path.join(process.cwd(), 'backend', 'api', 'interface.py'),
        JSON.stringify(data)
      ]);

      let result = '';
      let error = '';
      
      pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        error += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          console.error('Python process error:', error);
          reject(NextResponse.json({ error: 'Analysis failed' }, { status: 500 }));
          return;
        }

        try {
          const jsonResult = JSON.parse(result);
          resolve(NextResponse.json(jsonResult));
        } catch (e) {
          console.error('Failed to parse Python output:', result);
          reject(NextResponse.json({ error: 'Invalid response format' }, { status: 500 }));
        }
      });
    });
  } catch (error) {
    console.error('API route error:', error);
    return NextResponse.json({ error: 'Request failed' }, { status: 500 });
  }
}