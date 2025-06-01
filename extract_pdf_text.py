import fitz  # PyMuPDF
import os

pdf_dir = "pdfs"
output_dir = "texts"
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(pdf_dir):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_dir, filename)
        text_path = os.path.join(output_dir, filename.replace(".pdf", ".txt"))

        try:
            with fitz.open(pdf_path) as doc:
                full_text = ""
                for page in doc:
                    full_text += page.get_text()

            with open(text_path, "w", encoding="utf-8") as f:
                f.write(full_text)

            print(f"✅ Extracted: {filename}")
        except Exception as e:
            print(f"❌ Error processing {filename}: {str(e)}")

print("\nExtraction complete! Check the 'texts' directory for the extracted text files.") 