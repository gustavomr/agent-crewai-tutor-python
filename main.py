import os
import zipfile
import tempfile
import glob
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

# Load environment variables from .env file
load_dotenv()

# Configuração da API
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables. Please check your .env file.")

llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.1
)

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

def main():
    """
    Main function to process zip file and run code correction.
    """
    # Get the directory where main.py is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Look for zip files in the same directory
    zip_files = glob.glob(os.path.join(script_dir, '*.zip'))
    
    if not zip_files:
        print("❌ No zip files found in the current directory.")
        print(f"📁 Looking in: {script_dir}")
        return
    
    print(f"📁 Found zip files in {script_dir}:")
    for i, zip_file in enumerate(zip_files, 1):
        print(f"  {i}. {os.path.basename(zip_file)}")
    
    # Use the first zip file found
    zip_path = zip_files[0]
    print(f"\n🔄 Processing: {os.path.basename(zip_path)}")
    
    codigo_aluno, temp_dir = process_zip_file(zip_path)
    
    if codigo_aluno is None:
        cleanup(temp_dir, zip_path)
        return
    
    # --- O INPUT: Código do Aluno ---
    # Now using the code extracted from the zip file

    # --- AGENTE REVISOR ---
    revisor_tecnico = Agent(
        role='Especialista em Quality Assurance (QA) Python',
        goal='Validar se o script cumpre todos os requisitos pedagógicos e técnicos exigidos.',
        backstory="""Você é um revisor rigoroso mas didático. Sua função é garantir que o 
        código não apenas funcione, mas que siga exatamente as regras de negócio 
        estabelecidas no enunciado do exercício.""",
        llm=llm,
        verbose=True
    )

    # --- TAREFA DE ANÁLISE ---
    tarefa_analise = Task(
        description=f"""
        Analise o código Python abaixo e verifique se ele cumpre os seguintes critérios:
        1. Valida se a entrada está entre -60 e +50?
        2. Permite redigitação em caso de erro? Seja explicíto com Sim ou Não e não deve ser levado em considerações melhorias.
        3. Calcula a média máxima anual corretamente?
        4. Conta meses com temp > 33°C (meses escaldantes)?
        5. Identifica e exibe o nome do mês (por extenso) com maior e menor temperatura?
        
        CÓDIGO PARA ANÁLISE:
        {codigo_aluno}
        """,
        expected_output="""Um relatório estruturado contendo:
        - Lista de requisitos atendidos e não atendidos.
        - No máximo 3 sugestões de melhoria no código em texto a serem enviadas ao aluno.
        - Não é necessário ter uma conclusão""",
        agent=revisor_tecnico
    )

    # --- EXECUÇÃO ---
    corretor_automatico = Crew(
        agents=[revisor_tecnico],
        tasks=[tarefa_analise],
        max_rpm=10  # Limita a 10 requisições por minuto para não estourar a A
    )

    resultado = corretor_automatico.kickoff()
    print("\n=== RESULTADO DA AVALIAÇÃO ===\n")
    print(resultado)
    
    # Save result to file
    with open('resultado.txt', 'w', encoding='utf-8') as f:
        f.write("=== RESULTADO DA AVALIAÇÃO ===\n\n")
        f.write(str(resultado))
    
    print("\n📄 Result saved to resultado.txt")
    
    # Clean up files after processing
    cleanup(temp_dir, zip_path)

if __name__ == "__main__":
    main()