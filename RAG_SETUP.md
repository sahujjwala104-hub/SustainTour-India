# SustainTour India — Full RAG setup (Windows)

## Install once
Open Command Prompt in the SustainTour_India project folder:

```cmd
py -m pip install -r requirements.txt
```

## Start the application

```cmd
py -m streamlit run app.py
```

Select **AI Policy Assistant** in the sidebar, open **Gemini API settings**, and paste your API key from https://aistudio.google.com/apikey. The key is entered into a password field and is not written to a file.

## What happens
The app extracts text from local policy PDFs, creates overlapping chunks, ranks them with TF-IDF vector similarity, sends the most relevant evidence to Gemini, and displays an answer with `[S1]` source references and PDF page numbers. `[T1]` references a state/year row in the tourism CSV.

## Important
- The API needs internet access and an available Gemini quota. API usage may incur costs depending on account/plan.
- If a model is unavailable, change the model name in the settings to one enabled for your API key.
- The Kerala PDF may be scanned and therefore unsearchable until OCR is performed.
- This is genuine retrieval-augmented **generation**, but uses TF-IDF vectors instead of neural embeddings. It does not claim to use FAISS, Chroma, or an embedding model.
- Keep API keys private; do not paste them into code or upload them to GitHub.
