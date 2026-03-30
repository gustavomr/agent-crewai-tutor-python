import os
import zipfile
import tempfile
import glob
import time
import argparse
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

# Load environment variables from .env file
load_dotenv()

def process_zip_file(zip_path):
    """
    Extract and process Python files from a zip archive.
    """
    temp_dir = tempfile.mkdtemp()
    python_files = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find all Python and Jupyter notebook files in the extracted content
        python_files = glob.glob(os.path.join(temp_dir, '**', '*.py'), recursive=True)
        notebook_files = glob.glob(os.path.join(temp_dir, '**', '*.ipynb'), recursive=True)
        
        # Combine both file types
        all_files = python_files + notebook_files
        
        if not all_files:
            print("❌ No Python (.py) or Jupyter notebook (.ipynb) files found in the zip archive.")
            return None, temp_dir
        
        # Read the first file found
        file_path = all_files[0]
        
        if file_path.endswith('.ipynb'):
            # For Jupyter notebooks, extract code from cells
            import json
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    notebook = json.load(f)
                
                # Extract code from all code cells
                code_cells = []
                for cell in notebook.get('cells', []):
                    if cell.get('cell_type') == 'code':
                        code_cells.extend(cell.get('source', []))
                
                codigo_aluno = '\n'.join(code_cells)
                print(f"✅ Found and loaded Jupyter notebook: {os.path.basename(file_path)}")
                
            except Exception as e:
                print(f"❌ Error reading Jupyter notebook: {e}")
                return None, temp_dir
        else:
            # For regular Python files
            with open(file_path, 'r', encoding='utf-8') as f:
                codigo_aluno = f.read()
            print(f"✅ Found and loaded Python file: {os.path.basename(file_path)}")
        
        return codigo_aluno, temp_dir
        
    except Exception as e:
        print(f"❌ Error processing zip file: {e}")
        return None, temp_dir

def cleanup(temp_dir, zip_path):
    """
    Clean up temporary files and the original zip file.
    """
    try:
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if os.path.exists(zip_path):
            os.remove(zip_path)
        print("🧹 Cleanup completed.")
    except Exception as e:
        print(f"⚠️  Warning during cleanup: {e}")

def extract_student_name(zip_filename):
    """
    Extract student name from zip filename.
    Removes .zip extension and returns the name.
    """
    return os.path.splitext(zip_filename)[0]

def analyze_student_code(codigo_aluno, student_name, llm, csv_file_path=None):
    """
    Analyze student code using CrewAI and return the result.
    """
    # Read CSV file content if provided
    csv_content = ""
    if csv_file_path and os.path.exists(csv_file_path):
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Filter specific lines for evaluation
            filtered_lines = []
            header = lines[0] if lines else ""
            filtered_lines.append(header)
            
            for line in lines[1:]:  # Skip header
                if line.strip():  # Skip empty lines
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        date_str = parts[0]
                        try:
                            # Parse date (format: DD/MM/YYYY)
                            day, month, year = date_str.split('/')
                            month = int(month)
                            year = int(year)
                            
                            # Include: months 4 and 5 of 1984, and month 4 of all years
                            if (year == 1984 and month in [4, 5]) or month == 4:
                                filtered_lines.append(line)
                        except ValueError:
                            continue
            
            csv_content = ''.join(filtered_lines)
            print(f"✅ CSV file filtered: {len(filtered_lines)-1} relevant lines loaded")
        except Exception as e:
            print(f"⚠️  Warning: Could not read CSV file {csv_file_path}: {e}")
    
    # --- AGENTE REVISOR ---
    revisor_tecnico = Agent(
        role='Especialista em Quality Assurance (QA) Python',
        goal='Validar se o script cumpre todos os requisitos pedagógicos e técnicos exigidos.',
        backstory="""Você é um revisor rigoroso mas didático. Sua função é garantir que o 
        código não apenas funcione, mas que siga exatamente as regras de negócio 
        estabelecidas no enunciado do exercício. Você terá que executar o programa do aluno para encontrar cada uma das letras do exercício""",
        llm=llm,
        verbose=True
    )

    # --- TAREFA DE ANÁLISE ---
    tarefa_analise = Task(
        description=f"""
        
Requisitos Funcionais (Itens A ao E). 
Item A: Verificar se o aluno usou open('arquivo.csv') ou similar e fez a leitura do arquivo CSV.

Item B: O programa permite filtrar por período (mês/ano inicial e final) e escolher o tipo de dado (Precipitação, Temp, etc)? Usando como entrada no mês inicial 4 e 5 e ano de 1984 é apresentado dados corres pondentes. Para a precipitação (item2) um valor possível é 15.3 no dia 27/05/1984.

Item C (Mês mais chuvoso): O aluno identificou o mês mais chuvoso de todo o arquivo? A resposta é 06/1998 com 291.10 mm de precipitação.

Item D e E (Médias 2006-2016): O cálculo está restrito ao intervalo de 11 anos? Foi calculado a média de cada ano? Foi calculado a média das médias? Para a média de um mes/ano para o mês 4 em abril de 2006 é 16 graus C ou bem bem proximo disso. Para a media das medias é 15.34 graus celsius.

Item E (Gráfico): O código utiliza bibliotecas como matplotlib ou plotly? Os eixos estão rotulados? Os valores foram exibidos?

ARQUIVO CSV DE REFERÊNCIA (dados filtrados para avaliação - meses 4 e 5 de 1984, e mês 4 de todos os anos):
{csv_content}

CÓDIGO DO ALUNO PARA ANÁLISE:
{codigo_aluno}
        """,
        expected_output="""Um relatório estruturado contendo:
        - Lista de requisitos atendidos e não atendidos. Para cada item avaliado coloque um SIM ou NÃO. Para os casos de NÃO informe o motivo.
        - No máximo 3 sugestões de melhoria no código em texto a serem enviadas ao aluno.
        - Favor no final do arquivo colocar para cada letra os valores que foram encontrados na execução do programa do aluno""",
        agent=revisor_tecnico
    )

    # --- EXECUÇÃO ---
    max_rpm = int(os.getenv("MAX_RPM", "10"))
    timeout = int(os.getenv("TIMEOUT", "10"))
    corretor_automatico = Crew(
        agents=[revisor_tecnico],
        tasks=[tarefa_analise],
        max_rpm=max_rpm,  # Limita requisições por minuto para não estourar a API
        timeout=timeout  # Timeout em segundos para cada análise
    )

    resultado = corretor_automatico.kickoff()
    return resultado

def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Analyze student code using AI')
    parser.add_argument('--groq', action='store_true', help='Use Groq as LLM provider')
    parser.add_argument('--openrouter', action='store_true', help='Use OpenRouter as LLM provider')
    parser.add_argument('--project-office-id', type=str, help='Project Office ID for class identification')
    return parser.parse_args()

def get_llm_provider(args):
    """
    Determine LLM provider based on command line arguments or environment variable.
    """
    if args.groq and args.openrouter:
        raise ValueError("Cannot specify both --groq and --openrouter. Please choose one.")
    elif args.groq:
        return "groq"
    elif args.openrouter:
        return "openrouter"
    else:
        # Default to environment variable or "groq" if not set
        return os.getenv("LLM_PROVIDER", "groq").lower()

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
    """
    Main function to process all zip files in downloads folder and generate individual results.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Get LLM provider selection
    llm_provider = get_llm_provider(args)
    if llm_provider not in ["groq", "openrouter"]:
        raise ValueError(f"Invalid LLM_PROVIDER '{llm_provider}'. Must be 'groq' or 'openrouter'.")

    # Get Project Office ID
    project_office_id = get_project_office_id(args)
    print(f"🏢 Project Office ID: {project_office_id}")

    # Configuração da API
    if llm_provider == "groq":
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables. Please check your .env file.")
        os.environ["GROQ_API_KEY"] = groq_api_key
    elif llm_provider == "openrouter":
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables. Please check your .env file.")
        os.environ["OPENROUTER_API_KEY"] = openrouter_api_key

    llm_model = os.getenv("LLM_MODEL", "groq/llama-3.3-70b-versatile")
    llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))

    # Adjust model name for OpenRouter if needed
    if llm_provider == "openrouter" and not llm_model.startswith("openrouter/"):
        # Convert groq model to openrouter equivalent
        if "llama-3.3-70b-versatile" in llm_model:
            llm_model = "openrouter/meta-llama/llama-3.3-70b-instruct"
        elif "llama-3.1-70b" in llm_model:
            llm_model = "openrouter/meta-llama/llama-3.1-70b-instruct"
        elif "llama-3.1-8b" in llm_model:
            llm_model = "openrouter/meta-llama/llama-3.1-8b-instruct"
        else:
            # Default to a good openrouter model if no mapping found
            llm_model = "openrouter/meta-llama/llama-3.3-70b-instruct"

    llm = LLM(
        model=llm_model,
        temperature=llm_temperature
    )

    print(f"🤖 Using LLM Provider: {llm_provider.upper()}")
    print(f"🧠 Model: {llm_model}")
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get the CSV file path
    csv_file_path = os.path.join(script_dir, "Anexo_Arquivo_Dados_Projeto_Logica_e_programacao_de_computadores.csv")
    
    # Check if CSV file exists
    if not os.path.exists(csv_file_path):
        print(f"⚠️  Warning: CSV file not found at {csv_file_path}")
        csv_file_path = None
    else:
        print(f"✅ CSV file found: {os.path.basename(csv_file_path)}")
    
    # Get the downloads folder path (inside the project)
    downloads_dir = os.path.join(script_dir, os.getenv("DOWNLOADS_DIRECTORY", "downloads"))
    
    # Look for zip files in the downloads folder
    zip_files = glob.glob(os.path.join(downloads_dir, '*.zip'))
    
    if not zip_files:
        print("❌ No zip files found in the Downloads folder.")
        print(f"📁 Looking in: {downloads_dir}")
        return
    
    print(f"📁 Found {len(zip_files)} zip files in Downloads folder:")
    for i, zip_file in enumerate(zip_files, 1):
        print(f"  {i}. {os.path.basename(zip_file)}")
    
    print(f"\n🔄 Processing all files...")
    
    # Process each zip file
    for zip_path in zip_files:
        zip_filename = os.path.basename(zip_path)
        student_name = extract_student_name(zip_filename)
        
        print(f"\n--- Processing: {zip_filename} (Student: {student_name}) ---")
        
        codigo_aluno, temp_dir = process_zip_file(zip_path)
        
        if codigo_aluno is None:
            # Generate result file with error message
            result_filename = f"resultado_{student_name}.txt"
            with open(result_filename, 'w', encoding='utf-8') as f:
                f.write(f"=== RESULTADO DA AVALIAÇÃO ===\n\n")
                f.write("❌ ERRO NA PROCESSAMENTO DO ARQUIVO\n\n")
                f.write("Não foi possível encontrar arquivos Python (.py) ou Jupyter notebook (.ipynb) ")
                f.write("no arquivo zip fornecido, ou ocorreu um erro durante a extração.\n\n")
                f.write("Por favor, verifique se o arquivo zip contém o código fonte ")
                f.write("nos formatos esperados (.py ou .ipynb).")
            
            print(f"❌ Failed to process {zip_filename}")
            print(f"📄 Error report saved to {result_filename}")
            
            cleanup(temp_dir, zip_path)
            continue
        
        # Analyze the code
        try:
            resultado = analyze_student_code(codigo_aluno, student_name, llm, csv_file_path)
            
            # Generate individual result file
            result_filename = f"resultado_{student_name}.txt"
            with open(result_filename, 'w', encoding='utf-8') as f:
                f.write(f"=== RESULTADO DA AVALIAÇÃO ===\n\n")
                f.write(str(resultado))
            
            print(f"✅ Analysis completed for {student_name}")
            print(f"📄 Result saved to {result_filename}")
            
        except Exception as e:
            # Generate result file with error message
            result_filename = f"resultado_{student_name}.txt"
            with open(result_filename, 'w', encoding='utf-8') as f:
                f.write(f"=== RESULTADO DA AVALIAÇÃO ===\n\n")
                f.write("❌ ERRO DURANTE A ANÁLISE DO CÓDIGO\n\n")
                f.write(f"Ocorreu um erro durante a análise do código: {str(e)}\n\n")
                f.write("Isso pode ter acontecido por:\n")
                f.write("- Problemas de conexão com a API\n")
                f.write("- Formato de código inválido\n")
                f.write("- Erros internos no processamento\n\n")
                f.write("Por favor, tente novamente ou verifique o código fonte.")
            
            print(f"❌ Analysis error for {student_name}: {str(e)}")
            print(f"📄 Error report saved to {result_filename}")
        
        # Clean up files after processing
        cleanup(temp_dir, zip_path)
        
        # Delay entre processamentos para evitar rate limit
        delay = int(os.getenv("DELAY_BETWEEN_PROCESSES", "10"))
        print(f"⏳ Waiting {delay} seconds before next analysis...")
        time.sleep(delay)
    
    print(f"\n🎉 All files processed successfully!")

if __name__ == "__main__":
    main()
