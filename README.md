# Vessel Processing App

A Next.js frontend with FastAPI backend for processing vessel emission data.

## Setup Instructions

### 1. Install Python Dependencies
```bash
pip install fastapi uvicorn pandas PyPDF2 pywin32
```

### 2. Start the Backend
```bash
cd scripts
python backend.py
```
The backend will run on http://127.0.0.1:8000

### 3. Start the Frontend
The Next.js app will run on http://localhost:3000

### 4. Usage
1. Enter vessel names (comma-separated)
2. Select export formats
3. Click "Process Vessels"

## Troubleshooting

- Make sure the backend is running before using the frontend
- Ensure all file paths in `vessel_processor.py` are correct for your system
- Check that Excel files exist in the specified input folder
- If you get "Failed to fetch" errors, verify the backend is running on port 8000
