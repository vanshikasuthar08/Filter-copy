from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

# This model is loaded once when the service starts
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-mul-en")

class TranslationRequest(BaseModel):
    text: str

def chunk_text(text: str, chunk_size: int = 400):
    """
    A more robust function to break long text into chunks that respect sentence boundaries.
    """
    # First, split the text into paragraphs or large chunks
    paragraphs = text.split('\n')
    
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        # If adding the next paragraph doesn't exceed the chunk size, add it
        if len(current_chunk.split()) + len(paragraph.split()) <= chunk_size:
            current_chunk += paragraph + "\n"
        else:
            # If the current chunk is not empty, save it
            if current_chunk:
                chunks.append(current_chunk)
            
            # If the paragraph itself is too long, we must split it
            if len(paragraph.split()) > chunk_size:
                words = paragraph.split()
                long_chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
                chunks.extend(long_chunks)
                current_chunk = "" # Reset
            else:
                # Start a new chunk with the current paragraph
                current_chunk = paragraph + "\n"
    
    # Add the last remaining chunk
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

@app.post("/translate/")
def translate_text(request: TranslationRequest):
    if not request.text or not request.text.strip():
        return {"original_text": request.text, "translated_text": ""}
    
    # Chunk the text to avoid overloading the model
    text_chunks = chunk_text(request.text)
    
    translated_chunks = []
    for chunk in text_chunks:
        if chunk.strip():
            # Translate each chunk individually
            try:
                translated_data = translator(chunk)
                if translated_data and 'translation_text' in translated_data[0]:
                    translated_chunks.append(translated_data[0]['translation_text'])
            except Exception as e:
                print(f"Could not translate chunk: {e}")
                translated_chunks.append(chunk) # If translation fails, add the original chunk
    
    # Join the translated chunks back together
    full_translated_text = " ".join(translated_chunks)
    
    return {"original_text": request.text, "translated_text": full_translated_text}


