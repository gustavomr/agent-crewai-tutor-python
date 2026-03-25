from typing import Optional
from api_client import CookieAPIClient
import json
import os
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# CONFIGURATION PARAMETERS
# =============================================================================

# API Endpoints
API_BASE_URL = os.getenv("API_BASE_URL", "https://opm.pucrs.br")
CORRECTION_FLOW_ENDPOINT = os.getenv("CORRECTION_FLOW_ENDPOINT", "/api/project-office-v2/correction-flow")
STUDENT_PHASE_ENDPOINT = os.getenv("STUDENT_PHASE_ENDPOINT", "/api/project-office-v2/student-phase")

# Request Parameters
PROJECT_OFFICE_ID = os.getenv("PROJECT_OFFICE_ID", "11820")
PERIOD_ID = os.getenv("PERIOD_ID", "20076")
PHASE_ORDERS = int(os.getenv("PHASE_ORDERS", "1"))  #1 = Fase 1, 2 = Fase 2, 3 = Fase 3,

STATUS_IDS = int(os.getenv("STATUS_IDS", "4"))  #4 = AGUARDANDO_AVALIACAO, 10 = AVALIADO

# File Paths
API_RESPONSE_FILE = os.getenv("API_RESPONSE_FILE", "api_response.json")  #all students
STUDENT_PHASE_DETAILS_FILE = os.getenv("STUDENT_PHASE_DETAILS_FILE", "student_phase_details.json")  #get more information about the student to get the attachments
DOWNLOADS_DIRECTORY = os.getenv("DOWNLOADS_DIRECTORY", "downloads")
COOKIE_FILE = os.getenv("COOKIE_FILE", "cookie.json")

# Download Settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "8192"))

def get_all_students():
    print("\n\n🔍  Getting all students")
    print("=" * 50)
    
    client = CookieAPIClient(cookie_file=COOKIE_FILE)
    
    # Parameters from configuration
    params = {
        "project_office_id": PROJECT_OFFICE_ID,
        "period_id": PERIOD_ID,
        "phase_orders": PHASE_ORDERS,
        "status_ids": STATUS_IDS,
    }
    
    print(f"🔍 DEBUG: Sending parameters: {params}")
    print(f"🔍 DEBUG: PHASE_ORDERS value: {PHASE_ORDERS} (type: {type(PHASE_ORDERS)})")
    
    try:
        print("📊 Fetching correction flow data with parameters...")
        response = client.get_json(CORRECTION_FLOW_ENDPOINT, params)
        
        print(f"✅ Success! Found response with keys: {list(response.keys())}")
        # Show some data structure info
        if 'data' in response:
            
            data = response['data']
            if isinstance(data, list):
                print(f"📋 Response contains {len(data)} items")
                if len(data) > 0:
                    print(f"📝 Sample item keys: {list(data[0].keys())}")
            elif isinstance(data, dict):
                print(f"📋 Response data structure: {list(data.keys())}")
        
        # Save response to file for inspection
        with open(API_RESPONSE_FILE, "w") as f:
            json.dump(response, f, indent=2)
        print(f"💾 Response saved to '{API_RESPONSE_FILE}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return response

def example_post_request():
    """Example POST request to evaluation endpoint."""
    print("\n\n📝 POST Request Example - Evaluation")
    print("=" * 50)
    
    client = CookieAPIClient(cookie_file=COOKIE_FILE)
    
  
    
    print("✅ Successfully authenticated!")
    
    # Evaluation POST data
    post_data = {
        "phase_id": 99943,
        "student_project_id": 62484,
        "period_id": 20051,
        "supervisor_id": 52,
        "delivered_late": False,
        "delivered_resend": False,
        "feedback": "<p><strong>ParabénsS!</strong></p>\n<p>Você conseguiu entregar todas as etapas do trabalho de forma correta. <br /><br />Como sugestões de melhoria:</p>\n<p class=\"p1\" style=\"margin: 0px; font-variant-numeric: normal; font-variant-east-asian: normal; font-variant-alternates: normal; font-size-adjust: none; font-kerning: auto; font-optical-sizing: auto; font-feature-settings: normal; font-variation-settings: normal; font-variant-position: normal; font-variant-emoji: normal; font-stretch: normal; font-size: 13px; line-height: normal; font-family: 'Helvetica Neue'; color: #000000;\">Implementar tratamento de exceções mais robusto para lidar com entradas inválidas do usuário (ex: entrada de texto em campos numéricos).\",</p>\n<p class=\"p1\" style=\"margin: 0px; font-variant-numeric: normal; font-variant-east-asian: normal; font-variant-alternates: normal; font-size-adjust: none; font-kerning: auto; font-optical-sizing: auto; font-feature-settings: normal; font-variation-settings: normal; font-variant-position: normal; font-variant-emoji: normal; font-stretch: normal; font-size: 13px; line-height: normal; font-family: 'Helvetica Neue'; color: #000000;\">Utilizar estruturas de dados mais eficientes para armazenar e processar os dados (ex: dicionários para armazenar temperaturas por mês).\",</p>\n<p class=\"p1\" style=\"margin: 0px; font-variant-numeric: normal; font-variant-east-asian: normal; font-variant-alternates: normal; font-size-adjust: none; font-kerning: auto; font-optical-sizing: auto; font-feature-settings: normal; font-variation-settings: normal; font-variant-position: normal; font-variant-emoji: normal; font-stretch: normal; font-size: 13px; line-height: normal; font-family: 'Helvetica Neue'; color: #000000;\">Melhorar a clareza e organização do código utilizando funções para separar as diferentes etapas do programa (entrada, processamento e saída de dados).\"</p>\n<p>Na <strong>Fase 2</strong>, você aprenderá sobre estruturas de dados, outras estruturas de repetição, e como trabalhar com gráficos! Essas novas habilidades permitirão que você crie programas ainda mais eficientes e visualmente interessantes.</p>\n<p>Continue com esse empenho, e você verá como seu conhecimento em programação se expandirá. Estamos ansiosos para ver suas próximas entregas!</p>\n<p>Vamos em frente!</p>",
        "release_feedback": False,
        "calculation_delay": False,
        "evaluation_modality": "INDIVIDUAL",
        "criteria": [
            {
                "criterion_id": 17257,
                "criterion_dimension_id": 33938
            },
            {
                "criterion_id": 17258,
                "criterion_dimension_id": 33942
            },
            {
                "criterion_id": 17259,
                "criterion_dimension_id": 33945
            },
            {
                "criterion_id": 17260,
                "criterion_dimension_id": 33948
            },
            {
                "criterion_id": 17261,
                "criterion_dimension_id": 33951
            }
        ],
        "grade": 3
    }
    
    try:
        print("📤 Making POST request to evaluation endpoint...")
        print(f"🎯 Endpoint: {API_BASE_URL}/api/project-office-v2/evaluation?phase_id=99943")
        print(f"📊 Data size: {len(str(post_data))} characters")
        
        # Make the POST request using the authenticated client
        response = client.post_json("/api/project-office-v2/evaluation?phase_id=99943", json_data=post_data)
        
  
        
    except Exception as e:
        print(f"❌ POST request failed: {e}")
        print(f"🔍 Error type: {type(e).__name__}")

def cookie_inspection():
    """Inspect cookie information."""
    print("\n\n🍪 Cookie Inspection")
    print("=" * 50)
    
    client = CookieAPIClient(cookie_file=COOKIE_FILE)
    cookie_info = client.get_cookies_info()
    
    print(f"📊 Total cookies loaded: {cookie_info['total_cookies']}")
    print(f"🔑 Cookie names: {cookie_info['cookie_names'][:5]}...")  # Show first 5
    print(f"🌐 Session cookies: {len(cookie_info['session_cookies'])}")
    
    # Show some important cookies
    important_cookies = ['__Secure-next-auth.session-token', 'cf_clearance', 'institution']
    for cookie_name in important_cookies:
        if cookie_name in client.cookies:
            value = client.cookies[cookie_name]
            print(f"🔐 {cookie_name}: {value[:50]}..." if len(value) > 50 else f"🔐 {cookie_name}: {value}")
    
    #check if the cookie is valid
    if (client.check_authentication(url="/project-office-v2/11820/correction-flow")):
        print("🔑 Cookie is valid")
    else:
        print("❌ Cookie is invalid")

def fetch_student_phase_details():
    """Fetch student phase details for each phase ID from filtered data."""
    print("\n\n📋 Fetching Student Phase Details")
    print("=" * 50)
    
    # Load the filtered data
    try:
        with open(API_RESPONSE_FILE, "r") as f:
            api_response = json.load(f)
    except FileNotFoundError:
        print(f"❌ {API_RESPONSE_FILE} not found. Please run get_all_students() first.")
        return
    
    if not api_response or "phases" not in api_response:
        print("❌ No phases data found in API response.")
        return
    
    # Get the phases array from the response
    filtered_data = api_response["phases"]
    
    if not filtered_data:
        print("❌ No phases found in the response.")
        return
    
    # Initialize the API client
    client = CookieAPIClient(cookie_file=COOKIE_FILE)

    
    print(f"🔍 Fetching details for {len(filtered_data)} phases...")
    
    all_student_phases = []
    period_id = PERIOD_ID  # Using the configured period_id
    
    for i, phase in enumerate(filtered_data, 1):
        phase_id = phase["id"]
        print(f"📡 Fetching phase {i}/{len(filtered_data)}: ID {phase_id}")
        
        try:
            # Make the API call
            params = {
                "phase_id": str(phase_id),
                "period_id": period_id
            }
            
            response = client.get_json(STUDENT_PHASE_ENDPOINT, params)
            
            # Add the phase_id to the response for reference
            response["phase_id"] = phase_id
            all_student_phases.append(response)
            
            print(f"✅ Successfully fetched phase {phase_id}")
            
        except Exception as e:
            print(f"❌ Error fetching phase {phase_id}: {e}")
            # Add error info to the list
            all_student_phases.append({
                "phase_id": phase_id,
                "error": str(e),
                "status": "failed"
            })
    
    # Save all student phase details to a file
    with open(STUDENT_PHASE_DETAILS_FILE, "w") as f:
        json.dump(all_student_phases, f, indent=2)
    
    print(f"\n💾 Saved {len(all_student_phases)} student phase details to '{STUDENT_PHASE_DETAILS_FILE}'")
    
    # Show summary
    successful = len([item for item in all_student_phases if "error" not in item])
    failed = len([item for item in all_student_phases if "error" in item])
    
    print(f"📊 Summary: {successful} successful, {failed} failed")
    
    return all_student_phases

def download_attachments():
    """Download all zip files from attachment URLs in student_phase_details.json."""
    print("\n\n📥 Downloading Attachments")
    print("=" * 50)
    
    # Load the student phase details
    try:
        with open(STUDENT_PHASE_DETAILS_FILE, "r") as f:
            student_phases = json.load(f)
    except FileNotFoundError:
        print(f"❌ {STUDENT_PHASE_DETAILS_FILE} not found. Please run fetch_student_phase_details() first.")
        return
    
    if not student_phases:
        print("❌ No student phase data found.")
        return
    
    # Create downloads directory
    downloads_dir = DOWNLOADS_DIRECTORY
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)
        print(f"📁 Created downloads directory: {downloads_dir}")
    
    # Initialize the API client for authentication
    client = CookieAPIClient(cookie_file=COOKIE_FILE)
    
    total_attachments = 0
    successful_downloads = 0
    failed_downloads = 0
    
    print(f"🔍 Processing {len(student_phases)} student phases...")
    
    for i, phase_data in enumerate(student_phases, 1):
        # Skip if this phase had an error
        if "error" in phase_data:
            print(f"⚠️  Skipping phase {phase_data.get('phase_id', 'unknown')} due to previous error")
            continue
        
        # Get student info for naming
        student_name = phase_data.get("student", {}).get("name", "unknown")
        phase_id = phase_data.get("student_phase", {}).get("id", "unknown")
        
        print(f"\n👤 Processing {i}/{len(student_phases)}: {student_name} (Phase {phase_id})")
        
        # Get attachments from student_phase
        student_phase = phase_data.get("student_phase", {})
        attachments = student_phase.get("attachments", [])
        
        if not attachments:
            print(f"   ℹ️  No attachments found for {student_name}")
            continue
        
        print(f"   📎 Found {len(attachments)} attachment(s)")
        
        for j, attachment in enumerate(attachments, 1):
            total_attachments += 1
            
            # Get attachment info
            original_name = attachment.get("original_name", f"attachment_{j}.zip")
            filename = attachment.get("filename", f"file_{j}.zip")
            url = attachment.get("url")
            
            if not url:
                print(f"   ❌ No URL found for attachment {j}")
                failed_downloads += 1
                continue
            
            # Create a safe filename
            safe_student_name = "".join(c for c in student_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_filename = f"{safe_student_name}_Phase{phase_id}_{original_name}"
            file_path = os.path.join(downloads_dir, safe_filename)
            
            print(f"   📥 Downloading: {original_name}")
            
            try:
                # Download the file using the authenticated client
                response = client.session.get(url, stream=True)
                response.raise_for_status()
                
                # Save the file
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                
                print(f"   ✅ Downloaded: {safe_filename}")
                successful_downloads += 1
                
            except Exception as e:
                print(f"   ❌ Failed to download {original_name}: {e}")
                failed_downloads += 1
    
    print(f"\n📊 Download Summary:")
    print(f"   📁 Downloads saved to: {downloads_dir}")
    print(f"   📎 Total attachments found: {total_attachments}")
    print(f"   ✅ Successful downloads: {successful_downloads}")
    print(f"   ❌ Failed downloads: {failed_downloads}")
    
    return {
        "total_attachments": total_attachments,
        "successful_downloads": successful_downloads,
        "failed_downloads": failed_downloads,
        "downloads_dir": downloads_dir
    }

def unzip_files():
    """Extract all zip files in the downloads directory."""
    print("\n\n📦 Extracting Zip Files")
    print("=" * 50)
    
    import zipfile
    import shutil
    
    downloads_dir = DOWNLOADS_DIRECTORY
    
    if not os.path.exists(downloads_dir):
        print(f"❌ Downloads directory '{downloads_dir}' not found.")
        return
    
    # Get all zip files in the downloads directory
    zip_files = [f for f in os.listdir(downloads_dir) if f.endswith('.zip')]
    
    if not zip_files:
        print(f"ℹ️  No zip files found in '{downloads_dir}'")
        return
    
    print(f"🔍 Found {len(zip_files)} zip file(s) to extract")
    
    successful_extractions = 0
    failed_extractions = 0
    
    for i, zip_filename in enumerate(zip_files, 1):
        zip_path = os.path.join(downloads_dir, zip_filename)
        
        # Create extraction directory (remove .zip extension)
        extraction_dir_name = zip_filename[:-4]  # Remove .zip extension
        extraction_dir = os.path.join(downloads_dir, extraction_dir_name)
        
        print(f"\n📦 Extracting {i}/{len(zip_files)}: {zip_filename}")
        
        try:
            # Create extraction directory
            if os.path.exists(extraction_dir):
                print(f"   ⚠️  Directory already exists, removing: {extraction_dir_name}")
                shutil.rmtree(extraction_dir)
            
            os.makedirs(extraction_dir)
            
            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Get list of files in the zip
                file_list = zip_ref.namelist()
                print(f"   📁 Found {len(file_list)} file(s) in zip")
                
                # Extract all files
                zip_ref.extractall(extraction_dir)
                
                # Show extracted files
                for file_name in file_list[:5]:  # Show first 5 files
                    print(f"   📄 {file_name}")
                if len(file_list) > 5:
                    print(f"   ... and {len(file_list) - 5} more files")
            
            print(f"   ✅ Successfully extracted to: {extraction_dir_name}")
            successful_extractions += 1
            
        except zipfile.BadZipFile:
            print(f"   ❌ Invalid zip file: {zip_filename}")
            failed_extractions += 1
        except Exception as e:
            print(f"   ❌ Error extracting {zip_filename}: {e}")
            failed_extractions += 1
    
    print(f"\n📊 Extraction Summary:")
    print(f"   📦 Total zip files: {len(zip_files)}")
    print(f"   ✅ Successful extractions: {successful_extractions}")
    print(f"   ❌ Failed extractions: {failed_extractions}")
    
    return {
        "total_zip_files": len(zip_files),
        "successful_extractions": successful_extractions,
        "failed_extractions": failed_extractions
    }

def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Download student submissions from API')
    parser.add_argument('--project-office-id', type=str, help='Project Office ID for class identification')
    return parser.parse_args()

def get_project_office_id(args):
    """
    Determine Project Office ID from command line arguments or environment variable.
    """
    if args.project_office_id:
        return args.project_office_id
    else:
        # Default to environment variable
        return os.getenv("PROJECT_OFFICE_ID", "11820")

def main():    
    # Parse command line arguments
    args = parse_arguments()
    
    # Get Project Office ID
    project_office_id = get_project_office_id(args)
    print(f"🏢 Project Office ID: {project_office_id}")
    
    # Update global PROJECT_OFFICE_ID for this session
    global PROJECT_OFFICE_ID
    PROJECT_OFFICE_ID = project_office_id    
    
    cookie_inspection()
    get_all_students_filtered_data = get_all_students()
    print(get_all_students_filtered_data)

    if (get_all_students_filtered_data["total"] > 0):
        fetch_student_phase_details()
        download_attachments()
     #   unzip_files()

    #example_post_request()
    
    
    print("\n\n✅ All examples completed!")
    print(f"💡 Check '{API_RESPONSE_FILE}' for the full API response")
    print(f"💡 Check '{STUDENT_PHASE_DETAILS_FILE}' for student phase details")
    print(f"💡 Check '{DOWNLOADS_DIRECTORY}/' directory for downloaded zip files")


if __name__ == "__main__":
    main() 