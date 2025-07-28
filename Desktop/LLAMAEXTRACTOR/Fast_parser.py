import os, json
from pathlib import Path
from dotenv import load_dotenv
from llama_parse import LlamaParse
from PIL import Image
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import tempfile
import asyncio
import nest_asyncio
import threading

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# ── 1.  Load API key ───────────────────────────────────────────────────
load_dotenv()
API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")
if not API_KEY:
    raise RuntimeError("The API key does not exist 😔")

# ── 2.  Custom parsing instruction ───────────────
INS = """
You are a highly proficient language model designed to convert pages from PDF, PPT and other files into structured markdown text. Your goal is to accurately transcribe text, represent formulas in LaTeX MathJax notation, and identify and describe images, particularly graphs and other graphical elements.

You have been tasked with creating a markdown copy of each page from the provided PDF or PPT image. Each image description must include a full description of the content, a summary of the graphical object.

Maintain the sequence of all the elements.

For the following element, follow the requirement of extraction:
for Text:
   - Extract all readable text from the page.
   - Exclude any diagonal text, headers, and footers.

for Text which includes hyperlink:
    -Extract hyperlink and present it with the text

for Formulas:
   - Identify and convert all formulas into LaTeX MathJax notation.

for Image Identification and Description:
   - Identify all images, graphs, and other graphical elements on the page.
   - If the image has graph , extract the graph as image . DO NOT convert it into a table or extract the wording inside the graph.
   - If image contains wording that is hard to extract , flag it with  instead of parsing.
   - If the image has a subtitle or caption, include it in the description.
   - If the image has a formula convert it into LaTeX MathJax notation.
   - If the image has a organisation chart , convert it into a hierachical understandable format.
   - If the image contain process flow , capture it as a whole image instead of separate into blocks of images.

for Table:
   - Try to retain the columns and structure of the table and extract it into markdown format.

# OUTPUT INSTRUCTIONS

- Ensure all formulas are in LaTeX MathJax notation.
- Exclude any diagonal text, headers, and footers from the output.
- For each image and graph, provide a detailed description,caption if there's any and summary.
"""

# ── 3.  Thread-local storage for parser instances ──────────────────────
thread_local = threading.local()

def get_parser():
    """Get a thread-local parser instance"""
    if not hasattr(thread_local, 'parser'):
        thread_local.parser = LlamaParse(
            api_key=API_KEY,
            system_prompt=INS,
            verbose=True,
            ignore_errors=False,
            do_not_cache=True,
        )
    return thread_local.parser

# ── 4.  Folder layout ─────────────────────────────────────────────────-
ROOT      = Path.cwd()
OUT_ROOT  = ROOT / "parsed"

# All output folders under parsed/
DIR_TEXT   = OUT_ROOT / "text"
DIR_IMAGES = OUT_ROOT / "images"
DIR_MD     = OUT_ROOT / "md"
DIR_JSON   = OUT_ROOT / "json"
DIR_TABLES = OUT_ROOT / "tables"

# ── 5.  Helper functions ───────────────────────────────────────────────
def setup_output_folders():
    """Clean and create fresh output folders"""
    print("🧹 Cleaning existing output folders...")
    if OUT_ROOT.exists():
        shutil.rmtree(OUT_ROOT)
        print("   ✅ Removed all existing parsed data")

    # Create all directories fresh
    for d in (DIR_TEXT, DIR_IMAGES, DIR_MD, DIR_JSON, DIR_TABLES):
        d.mkdir(parents=True, exist_ok=True)

def fix_images_for_system_compatibility(raw_img_folder):
    """Convert JPEG2000 images to system-compatible PNG files"""
    
    converted_count = 0
    failed_count = 0
    
    print(f"      🔧 Processing images...")
    
    for img_file in raw_img_folder.glob("*"):
        try:
            # Open the image (regardless of extension)
            with Image.open(img_file) as img:
                
                # Determine output filename - keep same name but ensure .png extension
                if img_file.suffix.lower() == '.png':
                    output_name = img_file.name
                else:
                    output_name = img_file.stem + '.png'
                
                output_path = DIR_IMAGES / output_name
                
                # Handle different color modes for PNG compatibility
                if img.mode == 'RGBA':
                    converted_img = img
                elif img.mode == 'P':
                    converted_img = img.convert('RGBA')
                elif img.mode in ('L', 'LA'):
                    converted_img = img.convert('RGB')
                else:
                    converted_img = img.convert('RGB')
                
                # Save as PNG with optimization
                converted_img.save(output_path, 'PNG', optimize=True, compress_level=6)
                
                print(f"         ✅ {img_file.name} → {output_name}")
                converted_count += 1
                
        except Exception as e:
            print(f"         ❌ Failed to convert {img_file.name}: {e}")
            failed_count += 1
    
    print(f"      📊 Converted: {converted_count}, Failed: {failed_count}")
    return converted_count

def extract_tables_from_pages(pages, page_counter):
    """Extract table content from pages and save as separate files"""
    
    table_count = 0
    
    for page in pages:
        page_num = page_counter[0]
        md_content = page.get("md", "")
        
        # Look for markdown tables in the content
        lines = md_content.split('\n')
        current_table = []
        in_table = False
        table_num = 1
        
        for line in lines:
            # Detect table rows (contain | characters)
            if '|' in line.strip() and line.strip().startswith('|') and line.strip().endswith('|'):
                current_table.append(line)
                in_table = True
            elif in_table and line.strip() == '':
                # Empty line after table - save current table
                if current_table:
                    table_content = '\n'.join(current_table)
                    table_file = DIR_TABLES / f"page_{page_num}_table_{table_num}.md"
                    table_file.write_text(table_content, encoding="utf-8")
                    print(f"         📊 Extracted table: page_{page_num}_table_{table_num}")
                    table_count += 1
                    table_num += 1
                
                current_table = []
                in_table = False
            elif in_table:
                # Line might be part of table (separator line)
                if set(line.strip().replace('|', '').replace('-', '').replace(':', '').replace(' ', '')) == set():
                    current_table.append(line)
                else:
                    # Not a table line, save current table if exists
                    if current_table:
                        table_content = '\n'.join(current_table)
                        table_file = DIR_TABLES / f"page_{page_num}_table_{table_num}.md"
                        table_file.write_text(table_content, encoding="utf-8")
                        print(f"         📊 Extracted table: page_{page_num}_table_{table_num}")
                        table_count += 1
                        table_num += 1
                    
                    current_table = []
                    in_table = False
        
        # Check if we ended with a table
        if current_table:
            table_content = '\n'.join(current_table)
            table_file = DIR_TABLES / f"page_{page_num}_table_{table_num}.md"
            table_file.write_text(table_content, encoding="utf-8")
            print(f"         📊 Extracted table: page_{page_num}_table_{table_num}")
            table_count += 1
        
        page_counter[0] += 1
    
    return table_count

def parse_pdf_sync(pdf_path):
    """Parse PDF synchronously in thread pool"""
    parser = get_parser()
    return parser.get_json_result(str(pdf_path))

def extract_images_sync(json_objs, download_path):
    """Extract images synchronously in thread pool"""
    parser = get_parser()
    return parser.get_images(json_objs, download_path=download_path)

async def process_pdfs_async(pdf_paths: List[Path]):
    """Process multiple PDF files asynchronously and save to output folders"""
    
    # Setup fresh output folders
    setup_output_folders()
    
    page_counter = [1]  # Global page counter across all PDFs
    all_json_data = []  # Collect all JSON data
    
    total_pages = 0
    total_images = 0
    total_tables = 0
    
    for pdf_path in pdf_paths:
        name = pdf_path.stem
        print(f"\n=== Parsing {pdf_path.name} ===")

        # Parse PDF using asyncio.to_thread to avoid event loop conflicts
        json_objs = await asyncio.to_thread(parse_pdf_sync, pdf_path)
        pages = json_objs[0]["pages"]
        
        # Add to combined JSON data
        all_json_data.extend(json_objs)

        # -- extract images ----------------------------------------------
        raw_img_folder = OUT_ROOT / "temp_images"
        raw_img_folder.mkdir(parents=True, exist_ok=True)
        
        # Extract images using asyncio.to_thread
        await asyncio.to_thread(extract_images_sync, json_objs, str(raw_img_folder))
        
        # Convert and move to final images folder
        if raw_img_folder.exists() and any(raw_img_folder.glob("*")):
            converted_count = fix_images_for_system_compatibility(raw_img_folder)
            if converted_count > 0:
                print(f"      🎉 Created {converted_count} system-compatible images")
                total_images += converted_count
        else:
            print("      ⚠️  No images found to convert")

        # Clean up temp images for this PDF
        if raw_img_folder.exists():
            shutil.rmtree(raw_img_folder)

        # -- save text and markdown per page ----------------------------
        for p in pages:
            current_page = page_counter[0]
            (DIR_TEXT / f"page_{current_page}.txt").write_text(p["text"], encoding="utf-8")
            (DIR_MD   / f"page_{current_page}.md").write_text(p["md"],   encoding="utf-8")
            page_counter[0] += 1

        # Reset page counter for table extraction
        table_page_counter = [page_counter[0] - len(pages)]
        
        # -- extract tables ---------------------------------------------
        table_count = extract_tables_from_pages(pages, table_page_counter)
        if table_count > 0:
            print(f"      📊 Extracted {table_count} tables")
            total_tables += table_count

        imgs_found = sum(len(p["images"]) for p in pages)
        total_pages += len(pages)
        print(f"   ↳ {len(pages)} pages | {imgs_found} image(s) | {table_count} table(s) saved")

    # -- Save combined JSON data ----------------------------------------
    (DIR_JSON / "all_data.json").write_text(json.dumps(all_json_data, indent=2))

    return {
        "total_pages": total_pages,
        "total_images": total_images, 
        "total_tables": total_tables,
        "files_processed": len(pdf_paths)
    }

# ── 7.  FastAPI Setup ──────────────────────────────────────────────────
app = FastAPI(title="PDF Parser API", description="Upload PDFs for parsing with LlamaParse")

@app.post("/upload-pdfs/")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    """
    Upload one or more PDF files for parsing
    """
    
    # Validate file types
    pdf_files = []
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
        pdf_files.append(file)
    
    if not pdf_files:
        raise HTTPException(status_code=400, detail="No valid PDF files provided")
    
    # Create temporary directory for uploaded files
    temp_dir = Path(tempfile.mkdtemp())
    pdf_paths = []
    
    try:
        # Save uploaded files to temporary directory
        for file in pdf_files:
            temp_file_path = temp_dir / file.filename
            with open(temp_file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            pdf_paths.append(temp_file_path)
            print(f"📁 Saved {file.filename} to temporary location")
        
        # Process the PDFs asynchronously
        print(f"🚀 Starting to process {len(pdf_paths)} PDF(s)...")
        results = await process_pdfs_async(pdf_paths)
        
        print("\n✅ Processing completed!")
        print("📁 parsed/text/     - Plain text files (page_1.txt, page_2.txt, etc.)")
        print("📁 parsed/images/   - System-compatible PNG images")
        print("📁 parsed/md/       - Markdown files (page_1.md, page_2.md, etc.)")
        print("📁 parsed/json/     - Combined JSON data (all_data.json)")
        print("📁 parsed/tables/   - Extracted tables (page_X_table_Y.md)")
        
        return JSONResponse(content={
            "message": "PDFs processed successfully",
            "results": results,
            "output_folders": {
                "text": "parsed/text/",
                "images": "parsed/images/", 
                "markdown": "parsed/md/",
                "json": "parsed/json/",
                "tables": "parsed/tables/"
            }
        })
    
    except Exception as e:
        print(f"❌ Error processing PDFs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDFs: {str(e)}")
    
    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print("🧹 Cleaned up temporary files")

@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "PDF Parser API",
        "description": "Upload PDF files to parse them with LlamaParse",
        "endpoints": {
            "POST /upload-pdfs/": "Upload one or more PDF files for parsing"
        }
    }

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up thread pool on shutdown"""
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)