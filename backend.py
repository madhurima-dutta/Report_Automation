# Updated backend.py

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from vessel_processor import run_vessel_processing

app = FastAPI()

# CORS so frontend (Next.js) can call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a mapping from frontend IDs to backend sheet names
# Make sure this mapping is accurate and complete
format_map = {
    "reporting": "Reporting Page",
    "eua": "EUA",
    "fuel-eu": "Fuel EU",
    "backup": "Backup",
}

@app.get("/")
def home():
    return {"message": "Hello from Vessel Processing Backend"}

@app.post("/process-vessel")
def process_vessel(
    vessel: str = Body(...),
    formats: list[str] = Body(...)
):
    # Translate the formats from frontend IDs to the correct sheet names
    selected_sheets = []
    
    # Check for the 'all' option first
    if "all" in formats:
        selected_sheets = ["Reporting Page", "EUA", "Fuel EU", "Backup"]
    else:
        for f in formats:
            # Use the mapping to get the correct sheet name
            sheet_name = format_map.get(f)
            if sheet_name:
                selected_sheets.append(sheet_name)
    
    # Check if any valid sheets were selected after translation
    if not selected_sheets:
        return {
            "owner": "Unknown",
            "message": "No valid sheets selected for processing.",
            "status": "error"
        }

    # Pass the correctly translated list to the processing function
    result_message = run_vessel_processing([vessel], selected_sheets)
    
    # Since run_vessel_processing returns a string message,
    # we'll return a placeholder for the owner.
    # The frontend is expecting a dictionary with `owner` and `message`.
    # You would need to modify `vessel_processor.py` to return the owner name
    # if you want to display it.
    return {
        "owner": "Unknown",
        "message": result_message,
    }