import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(req: NextRequest) {
  const data = await req.json();
  
  return new Promise((resolve) => {
    const pythonProcess = spawn('python', [
      path.join(process.cwd(), 'backend', 'api', 'interface.py'),
      JSON.stringify(data)
    ]);

    let result = '';
    
    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
    });

    pythonProcess.on('close', () => {
      resolve(NextResponse.json(JSON.parse(result)));
    });
  });
}