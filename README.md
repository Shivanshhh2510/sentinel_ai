# SentinelAI — AI Data Analytics Copilot

SentinelAI is an AI-powered **Data Analytics Copilot** that allows users to upload datasets and ask questions in natural language to automatically generate insights, charts, and statistical analysis.

The system combines **FastAPI, Machine Learning, Statistical Analysis, and Intelligent Query Understanding** to transform raw datasets into actionable business insights.

The long-term vision of SentinelAI is:

> **“ChatGPT for Data Analysis.”**

Users can upload datasets and ask questions such as:

- average revenue by region  
- top 5 products by revenue  
- revenue trend over time  
- correlation between price and demand  

SentinelAI automatically generates:

- Statistical insights  
- Charts and visualizations  
- Trend analysis  
- Executive-level explanations  

---

# Project Overview

Traditional data analysis tools require knowledge of **SQL, Python, or BI platforms**.

SentinelAI removes this barrier by allowing users to simply **ask questions about their dataset**.

### Example queries

- revenue by region  
- average sales by category  
- top 3 products by revenue  
- revenue trend over time  

The system automatically:

- Understands the intent of the question  
- Executes deterministic analytical queries  
- Generates charts and visualizations  
- Produces statistical insights and explanations  

---

# Key Features

## Natural Language Data Queries

Users can query datasets using natural language.

### Examples

- average revenue by region  
- top 3 regions by revenue  
- revenue trend  
- show important charts  

The system automatically:

- Detects the analytical intent  
- Extracts metric and grouping columns  
- Executes aggregation queries  
- Generates insights and visualizations  

---

## Automatic Chart Generation

SentinelAI automatically generates visualizations based on the query.

### Supported chart types

- Bar charts  
- Line charts  
- Scatter plots  
- Trend charts  

### Example

Query:

```
revenue by region
```

Output:

- Bar chart  
- Statistical insights  

---

## Trend Intelligence Engine

SentinelAI analyzes time-series data and detects patterns such as:

- Growth phases  
- Volatility levels  
- Momentum signals  
- Risk indicators  

### Example output

- Growth Phase: Severe Decline  
- Volatility Index: High Instability  
- Momentum Signal: Acceleration detected  

---

## Dataset Profiling Engine

When a dataset is uploaded, SentinelAI automatically performs **dataset profiling**.

Detection includes:

- Numeric columns  
- Categorical columns  
- Datetime columns  
- Missing values  
- Duplicate rows  
- Identifier columns  
- High-cardinality columns  

This allows the system to intelligently understand the dataset structure before performing analysis.

---

## Insight Discovery Engine

Users can request automatic dataset insights.

### Example query

```
give me insights
```

SentinelAI automatically detects patterns such as:

- Top performing categories  
- Value ranges  
- Average metrics  
- Distribution statistics  

---

## Automatic Chart Recommendations

Users can request recommended charts for their dataset.

### Example query

```
show important charts
```

SentinelAI generates key analytical charts such as:

- Sales by Region  
- Revenue Trend  
- Units Sold vs Price correlation  

---

# System Workflow

```
User
  │
  ▼
Dataset Upload (CSV / Excel)
  │
  ▼
Dataset Profiling Engine
  │
  ▼
Natural Language Query
  │
  ▼
Intent Detection
  │
  ▼
Query Planner
  │
  ▼
Analytics Engine
  │
  ▼
Chart Generator + Insight Engine
  │
  ▼
Structured Response (Charts + Insights)
```

---

# Project Architecture

```
User
  │
  ▼
FastAPI Backend
  │
  ├── Dataset Upload Engine
  ├── Dataset Profiling Engine
  ├── Intent Detection Engine
  ├── Query Planning Engine
  ├── Deterministic Analytics Engine
  ├── Chart Generation Engine
  └── Insight Generation Engine
  │
  ▼
PostgreSQL Database
```

---

# Tech Stack

## Backend

- FastAPI  
- Python 3.10+  
- SQLAlchemy  
- Alembic  

## Data Processing

- Pandas  
- NumPy  

## Machine Learning / Analytics

- Scikit-learn  

## Database

- PostgreSQL  

## Caching

- Redis  

---

# How to Run the Project Locally

## 1. Clone the Repository

```bash
git clone https://github.com/Shivanshhh2510/sentinel_ai.git
cd sentinel_ai
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate environment.

### Windows

```bash
venv\Scripts\activate
```

### Mac / Linux

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the root directory.

Example:

```
DATABASE_URL=postgresql://username:password@localhost:5432/sentinelai
REDIS_URL=redis://localhost:6379
```

---

## 5. Run Database Migrations

```bash
alembic upgrade head
```

---

## 6. Start Backend Server

```bash
uvicorn app.main:app --reload
```

Backend will start at:

```
http://127.0.0.1:8000
```

---

## 7. Access API Documentation

FastAPI automatically provides API documentation.

Open:

```
http://127.0.0.1:8000/docs
```

From here you can test:

- dataset upload  
- dataset queries  
- analytics endpoints  

---

# Example API Query

### Endpoint

```
POST /datasets/{dataset_id}/query
```

### Request Body

```json
{
  "question": "average revenue by region"
}
```

### Example Response

```json
{
  "type": "chart",
  "chart": {
    "chart_type": "bar",
    "title": "mean revenue by region"
  },
  "insight": "North currently leads revenue performance."
}
```

---

# Project Structure

```
sentinel_ai
│
├── app
│   ├── analytics
│   ├── chat
│   ├── ingestion
│   ├── profiling
│   ├── routes
│   ├── services
│   └── models
│
├── alembic
│
├── uploads
│
├── requirements.txt
└── README.md
```

---

# Future Roadmap

SentinelAI will evolve into a **full AI analytics platform**.

Planned features include:

- Conversational analytics  
- AI dashboard generation  
- AutoML model training  
- Prediction engine  
- Vector search over datasets  
- Multi-user SaaS platform  

---

# Author

**Shivansh Mishra**  
AI / Data Science Engineer  
B.Tech Computer Science  

Currently building **SentinelAI — AI Data Analytics Copilot**
