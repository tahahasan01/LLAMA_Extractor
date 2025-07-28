# 🦙 LlamaParse PDF Extraction System

A powerful PDF parsing system built with [Llama Cloud’s LlamaParse](https://cloud.llamaindex.ai/), designed to extract structured content from documents including markdown, tables, images, formulas, and plain text.

Supports both:
- ✅ Batch mode for local PDFs
- ✅ Real-time PDF uploads via a FastAPI server

---

## 🚀 Features

- 📄 Batch parsing of all PDFs in a folder  
- 📤 API endpoint for PDF upload and dynamic parsing  
- 🧠 Structured Markdown conversion  
- 📊 Table extraction as Markdown  
- 🖼️ Chart/image extraction and format correction (e.g., JPEG2000 to PNG)  
- 🧮 Formula rendering to LaTeX  
- 📂 Organized output in `/parsed` folder  

---

## 📁 Folder Structure

LLAMA_Extractor/
├── Data/ # Folder with input PDFs
├── parsed/ # Output folder
│ ├── md/ # Structured markdown files
│ ├── text/ # Plain text output
│ ├── tables/ # Extracted tables
│ ├── images/ # Images from PDFs
│ └── json/ # Full raw JSON output
├── .env # Your API key for LlamaParse
├── batch_llamaparse.py # Batch parsing script
├── main.py # FastAPI server for uploads
└── requirements.txt # Python dependencies

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/tahahasan01/LLAMA_Extractor.git
cd LLAMA_Extractor
2. Create and Activate a Virtual Environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
3. Install Dependencies
pip install -r requirements.txt
4. Set Your API Key
Create a .env file in the project root:
LLAMA_CLOUD_API_KEY=your_llama_api_key_here
🛠️ Usage
🅰️ Batch Mode (Parse All PDFs in Data/ Folder)
python batch_llamaparse.py
🅱️ API Mode (Run FastAPI Server)
python main.py
Open browser at: http://localhost:8000/docs

Upload PDFs using the Swagger UI or via HTTP POST.

📦 Output Structure
Each parsed PDF generates:

✅ .md (Structured Markdown)
✅ .txt (Plain text)
✅ .png images (converted if needed)
✅ Markdown tables
✅ .json (Full parsed document from LlamaParse)

📄 Requirements
Python 3.8+
FastAPI
python-dotenv
llama-index
llama-parse
uvicorn
Pillow

📌 License
MIT License. See LICENSE for details.

✨ Acknowledgements
LlamaIndex
LlamaParse
Inspired by real-world document processing & RAG use-cases.
