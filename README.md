# SustainTour India

SustainTour India is a data-driven platform for exploring tourism patterns and sustainable tourism planning across Indian States and Union Territories.

Built with Streamlit, the project combines tourism statistics with environmental and development indicators, interactive visualisations, machine learning, scenario planning, and an AI-powered tourism policy assistant.

## Features

### Tourism Intelligence

Explore domestic and foreign tourism across India using historical data from 2011–2025.

- State-wise tourism rankings
- Interactive India choropleth maps
- Domestic and foreign tourist visit trends
- Year-on-year growth analysis
- State comparisons
- Tourism anomaly detection
- Downloadable tourism data

### Sustainability Intelligence

Compare tourism demand with state-level sustainability indicators, including:

- Forest cover
- Groundwater extraction
- SDG scores
- Total tourist visits

These indicators provide environmental and development context and are not treated as impacts directly caused by tourism.

### State Comparison

Compare multiple States and Union Territories using tourism and sustainability indicators through interactive charts and tables.

### Machine Learning Intelligence

The platform includes two exploratory machine-learning components:

- Tourism demand forecasting using a damped log-linear trend model
- K-Means clustering of states based on tourism volume, growth, volatility, and foreign visitor share

Forecast performance can also be evaluated using historical backtesting with MAE and RMSE.

### Sustainable Planning Studio

An interactive scenario simulator allows users to redistribute a percentage of domestic tourism demand from one state to selected destination states.

It can be used to explore how alternative tourism distributions affect tourism concentration.

The simulator represents a planning scenario and does not predict actual traveller behaviour or destination carrying capacity.

### AI Policy Assistant

The Tourism Policy Assistant uses Retrieval-Augmented Generation (RAG) to answer questions using tourism policy documents.

The pipeline uses:

- PDF text extraction
- TF-IDF vectorisation
- Cosine-similarity retrieval
- Google Gemini for answer generation
- Source citations and retrieved evidence

The current knowledge base includes national sustainable tourism policy material, Kerala responsible tourism policy material, and tourism statistics from the project dataset.

## Dataset

The main tourism dataset contains:

- Tourism data from 2011–2025
- 36 Indian States and Union Territories
- Domestic tourist visits
- Foreign tourist visits
- Total tourist visits
- Foreign visitor share
- Year-on-year tourism growth

Additional sustainability data is sourced from organisations including the Forest Survey of India, Central Ground Water Board, and NITI Aayog.

## Data Sources

The project uses data from official and institutional sources including:

- Ministry of Tourism, Government of India
- India Tourism Data Compendium 2026
- Reserve Bank of India
- Forest Survey of India
- Central Ground Water Board
- NITI Aayog SDG India Index

## Tech Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- Scikit-learn
- PyPDF
- Google Gemini API
- GeoJSON

## Project Structure

```text
SustainTour-India/
├── app.py
├── requirements.txt
├── data/
│   ├── geo/
│   └── processed/
├── frontend/
├── reports/
├── research/
│   └── policies/
├── scripts/
└── src/
    ├── anomaly_detection.py
    ├── charts.py
    ├── data_loader.py
    ├── geo_utils.py
    ├── metrics.py
    └── views/
```

## Installation

Clone the repository:

```bash
git clone https://github.com/sahujjwala104-hub/SustainTour-India.git
cd SustainTour-India
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Run the Streamlit app using:

```bash
streamlit run app.py
```

Streamlit will provide a local URL where the application can be accessed.

## AI Policy Assistant Setup

The AI Policy Assistant requires a Google Gemini API key for generated answers.

Set the following environment variable:

```text
GEMINI_API_KEY=your_api_key_here
```

The API key can also be entered through the application interface.

Do not commit API keys to the repository.

## Limitations

- Tourist visit figures represent reported visits rather than necessarily unique tourists.
- Sustainability indicators come from different reference years.
- Environmental indicators should not be interpreted as environmental impacts directly caused by tourism.
- Forecasts are exploratory estimates and can be affected by exceptional events such as COVID-19 or major tourism events.
- Planning scenarios do not model actual traveller behaviour or destination carrying capacity.
- AI-generated policy responses should be verified against the retrieved source material.

## Future Scope

Potential extensions include:

- District-level tourism analysis
- Destination carrying-capacity indicators
- Carbon-footprint estimation
- Transport accessibility analysis
- Seasonal tourism forecasting
- Semantic embedding-based policy retrieval
- Sustainable itinerary and destination recommendations

## Purpose
SustainTour India demonstrates how tourism data, sustainability indicators, machine learning, interactive visualisation, scenario modelling, and policy intelligence can be combined to support more informed sustainable tourism planning.
