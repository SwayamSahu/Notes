Key features of the PDF Data Extraction (Traditional ML)
 
1. Detect and correct skew angles
2. Rotate misaligned pages
3. Perform high-quality OCR using multiple engines (Tesseract, PaddleOCR, EasyOCR)
4. Extract text with word-level precision
5. Identify special patterns (dates, numbers, codes, etc.)
6. Support various table structures
7. Generate corrected output PDFs
 
 
Key features of the Invoice Text Classification System (Using LLM)
 
1. Classifies invoice items as Product or Service using LLaMA via LangChain.
2. Generates context-aware summaries for user queries.
3. Uses Excel input and stores embeddings in a Chroma vector DB.
4. Offers a CLI with real-time classification and intelligent query handling (Given apt dataset).
5. Runs locally using Ollama models (llama3.2, mxbai-embed-large).


Key features of the CAPTCHA Text Extraction (Traditional ML)
 
1. Extracts CAPTCHA text using Tesseract OCR.
2. Uses CNN fallback if OCR fails.
3. Applies image preprocessing (adaptive thresholding, denoising, and morphological ops) for accuracy.
