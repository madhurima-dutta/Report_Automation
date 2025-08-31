import os
import pandas as pd
from datetime import datetime
from PyPDF2 import PdfMerger
import pythoncom
import win32com.client as win32

# ---- Get user home directory dynamically ----
home_dir = os.path.expanduser("~")

# ---- Dynamic output folders based on current month ----
base_pdf_folder = os.path.join(
    home_dir,
    "CSMCY Dropbox",
    "Columbia Control Room",
    "Emissions",
    "Emission Statements",
    "2025",
    "Emission Statements - 2025",
    "PDF"
)

base_xls_folder = os.path.join(
    home_dir,
    "CSMCY Dropbox",
    "Columbia Control Room",
    "Emissions",
    "Emission Statements",
    "2025",
    "Emission Statements - 2025",
    "XLS"
)

current_month = datetime.now().strftime("%B")  # e.g., "August"
pdf_output_folder = os.path.join(base_pdf_folder, f"{current_month} - 2025")
xls_output_folder = os.path.join(base_xls_folder, f"{current_month} - 2025")

# ---- Load vessel-owner mapping ----
mapping_file = os.path.join(
    home_dir,
    "CSMCY Dropbox",
    "Columbia Control Room",
    "Emissions",
    "Emission Statements",
    "2025",
    "EU Port Data",
    "Vessel-Owner List",
    "Vessel and Owner.xlsx"
)
mapping_df = pd.read_excel(mapping_file)

# Assuming columns are "Vessel" and "Owner"
mapping_df["Vessel"] = mapping_df["Vessel"].str.upper().str.strip()
vessel_to_owner = dict(zip(mapping_df["Vessel"], mapping_df["Owner"]))


def kill_excel_processes():
    """Kill any hanging Excel processes"""
    import subprocess
    try:
        subprocess.run(['taskkill', '/f', '/im', 'excel.exe'],
                      capture_output=True, check=False)
    except:
        pass


def export_vessel_sheets(input_folder, pdf_output_folder, xls_output_folder, vessel_name, sheet_names):
    """
    Export selected sheets from a vessel's Excel file.
    - Normal sheets are exported as PDF (merged into one file)
    - Backup sheet is saved as separate Excel file
    """

    kill_excel_processes()
    pythoncom.CoInitialize()

    owner_name = vessel_to_owner.get(vessel_name, vessel_name)  # Fallback to vessel name if not found
    owner_folder_name = owner_name.replace(" - ", "_").replace(" ", "_")  # Clean folder name
    
    owner_pdf_folder = os.path.join(pdf_output_folder, owner_folder_name)
    owner_xls_folder = os.path.join(xls_output_folder, owner_folder_name)

    # ---- Secondary backup path (dynamic) ----
    secondary_backup_base = os.path.join(
        home_dir,
        "CSMCY Dropbox",
        "Columbia Control Room",
        "ETS_Commercial Consideration",
        "Fuelink - 2025",
        f"{current_month} - 2025"
    )
    secondary_backup_folder = os.path.join(secondary_backup_base, owner_folder_name)

    os.makedirs(owner_pdf_folder, exist_ok=True)
    os.makedirs(owner_xls_folder, exist_ok=True)
    os.makedirs(secondary_backup_folder, exist_ok=True)  # Create secondary backup folder

    excel = None
    workbook = None

    try:
        excel = win32.gencache.EnsureDispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        excel.EnableEvents = False
        excel.ScreenUpdating = False

        vessel_file = None
        for file in os.listdir(input_folder):
            if file.endswith((".xlsx", ".xlsm")) and vessel_name in file.upper():
                vessel_file = os.path.join(input_folder, file)
                break

        if not vessel_file:
            return

        print("✅ Folder found")
        workbook = excel.Workbooks.Open(vessel_file)

        # Temporary PDFs to merge later
        temp_pdfs = []

        for sheet_name in sheet_names:
            try:
                sheet = workbook.Sheets(sheet_name)

                if sheet_name.lower() == "backup":
                    output_file = os.path.join(
                        owner_xls_folder,
                        f"{os.path.splitext(os.path.basename(vessel_file))[0]}_{sheet_name}.xlsx"
                    )
                    secondary_output_file = os.path.join(
                        secondary_backup_folder,
                        f"{os.path.splitext(os.path.basename(vessel_file))[0]}_{sheet_name}.xlsx"
                    )
                    
                    new_wb = excel.Workbooks.Add()
                    sheet.Copy(Before=new_wb.Sheets(1))

                    for s in list(new_wb.Sheets):
                        if s.Name != sheet_name:
                            try:
                                s.Delete()
                            except:
                                pass

                    new_wb.SaveAs(output_file)
                    new_wb.SaveAs(secondary_output_file)
                    new_wb.Close(SaveChanges=False)
                    print("✅ Backup saved to both locations")

                else:
                    temp_pdf = os.path.join(
                        owner_pdf_folder,
                        f"__temp_{sheet_name}.pdf"
                    )
                    sheet.ExportAsFixedFormat(
                        Type=0,  # xlTypePDF
                        Filename=temp_pdf,
                        Quality=0,  # xlQualityStandard
                        IncludeDocProperties=True,
                        IgnorePrintAreas=False,
                        OpenAfterPublish=False
                    )
                    temp_pdfs.append(temp_pdf)
                    print(f"✅ {sheet_name} saved")

            except:
                pass

        # Merge PDFs if there are any
        if temp_pdfs:
            merged_pdf = os.path.join(
                owner_pdf_folder,
                f"{os.path.splitext(os.path.basename(vessel_file))[0]}.pdf"
            )
            merger = PdfMerger()
            for pdf in temp_pdfs:
                merger.append(pdf)
            merger.write(merged_pdf)
            merger.close()

            for pdf in temp_pdfs:
                os.remove(pdf)

            print("✅ All saved")

    except:
        pass

    finally:
        try:
            if workbook:
                workbook.Close(SaveChanges=False)
            if excel:
                excel.DisplayAlerts = True
                excel.EnableEvents = True
                excel.ScreenUpdating = True
                excel.Quit()
        except:
            pass

        pythoncom.CoUninitialize()
        kill_excel_processes()


# ---- Input folder (dynamic) ----
input_folder = os.path.join(
    home_dir,
    "CSMCY Dropbox",
    "Columbia Control Room",
    "Emissions",
    "Emission Statements",
    "2025",
    "Emission Data - 2025"
)


if __name__ == "__main__":
    # ---- User Input ----
    vessel_input = input("Enter vessel name(s) in BLOCK letters (comma-separated for multiple, e.g. FRONT CHEETAH, AAL BRISBANE): ").strip().upper()
    vessel_names = [name.strip() for name in vessel_input.split(",")]

    print("\nSelect the sheets to export:")
    print("1. Reporting Page")
    print("2. EUA")
    print("3. Fuel EU")
    print("4. Backup (saved as Excel)")
    print("5. All (Reporting Page + EUA + Fuel EU + Backup)")

    choice = input("Enter choice numbers (comma separated, e.g. 1,2): ").strip()

    # Map choices
    choice_map = {"1": "Reporting Page", "2": "EUA", "3": "Fuel EU", "4": "Backup"}
    if "5" in choice.split(","):
        selected_sheets = ["Reporting Page", "EUA", "Fuel EU", "Backup"]
    else:
        selected_sheets = [choice_map[c.strip()] for c in choice.split(",") if c.strip() in choice_map]

    if selected_sheets:
        for vessel_name in vessel_names:
            print(f"\n--- Processing vessel: {vessel_name} ---")
            export_vessel_sheets(input_folder, pdf_output_folder, xls_output_folder, vessel_name, selected_sheets)
        
        print(f"\n✅ All {len(vessel_names)} vessel(s) processed successfully!")

def run_vessel_processing(vessel_names=None, selected_sheets=None):
    """
    Wrapper to run the vessel processing logic programmatically
    instead of using manual input().
    """
    if not vessel_names:
        return {"error": "No vessel names provided"}
    if not selected_sheets:
        return {"error": "No sheets selected"}

    for vessel_name in vessel_names:
        print(f"\n--- Processing vessel: {vessel_name} ---")
        export_vessel_sheets(input_folder, pdf_output_folder, xls_output_folder, vessel_name, selected_sheets)

    return f"✅ Processed {len(vessel_names)} vessel(s) successfully!"
