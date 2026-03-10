# Oil Intelligence Index implementation Plan

This project aims to build an intelligence aggregator that functions similarly to the "Bitcoin Fear & Greed Index," but specialized for the oil market. Instead of user sentiment, it will rely on real-world Open-Source Intelligence (OSINT) data, such as real-time supply metrics and major conflict events.

## Core Objective
To aggregate high-value, non-delayed news and data sources, evaluate their relevance to global oil supply chain disruptions, and output a quantifiable "Buy or Sell" indicator accompanied by the supporting intelligence.

## System Architecture

The application will consist of three main components:

1.  **Data Ingestion Hub (The Scrapers & API integrations)**
2.  **Intelligence Analysis Engine (AI/NLP & Scoring)**
3.  **The Dashboard Frontend**

---

### 1. Data Ingestion Hub

We will ingest data from specific, high-signal sources.

*   **Conflict & Geopolitical Events:**
    *   **Source:** Telegram specific channels (e.g., military bloggers, local raw feeds) and OSINT Twitter accounts.
    *   **Mechanism:** Telegram MTProto API (or Telethon in Python) and X/Twitter API (or snscrape/nitter).
*   **Physical Supply & Logistics:**
    *   **Source:** Real-time AIS (vessel tracking) APIs to monitor oil tanker movements, delays at major choke points (e.g., Strait of Hormuz, Suez Canal).
    *   **Source:** NASA FIRMS (Fire Information for Resource Management System) to detect immediate refinery or pipeline attacks/explosions.
*   **Macro Economic / Official Supply Data:**
    *   **Source:** APIs for EIA (U.S. Energy Information Administration) or OPEC reports (though these are often delayed, they provide baselines).

### 2. Intelligence Analysis Engine (The Core Logic)

This is the backend service (likely Python or Node.js) that processes the raw data into the final indicator.

*   **Step 1: AI Filtering & Verification:** When a piece of news or a data point comes in, pass it through an LLM (e.g., OpenAI, Claude, or a local model) to determine:
    1.  Is this event real or fake (cross-reference with multiple sources)?
    2.  Is this directly related to oil supply, production, or transport?
*   **Step 2: Scoring Mechanism (The Algorithm):** 
    *   Each verified event is given a **Relevance Score (1-10)** based on its potential to disrupt supply (e.g., an attack on a major Saudi facility is a 10; a minor political statement is a 2).
    *   Each event is assigned a **Signal Direction (-1 to +1)**. 
        *   `-1` (Bearish/Sell) = Oversupply, peace treaties, SPR releases.
        *   `+1` (Bullish/Buy) = Supply disruption, pipeline attacks, war escalation in oil-producing regions.
*   **Step 3: Calculating the Index:** The final index (e.g., 0-100, where 0 is Strong Sell, 100 is Strong Buy) is calculated using a weighted moving average of all recent events, heavily weighted towards high-relevance, recent events.

### 3. Dashboard Frontend (The UI)

A clean, minimalist web application (Next.js or Vite/React + TailwindCSS).

*   **The Main Indicator (Hero Section):** A gauge chart prominently displaying the current Index status: "Strong Sell," "Sell," "Neutral," "Buy," or "Strong Buy."
*   **The Intelligence Feed:** A scrolling, real-time feed of the processed events. For each event, it displays:
    *   The raw headline/data point.
    *   The AI-assigned **Relevance Score**.
    *   The **Signal Direction** (Bullish/Bearish tag).
    *   The original source (Telegram link, Satellite image, etc.).
*   **Metrics Dashboard:** Small widgets showing current vessel traffic bottlenecks or recent anomalies (e.g., "3 abnormal refinery fires detected today").

## Next Development Steps

1.  **Initialize Project Repository:** Set up a Next.js full-stack application.
2.  **Build a Basic Scraper:** Start with one specific source (e.g., a known OSINT RSS feed or a sample Telegram channel) to test the ingestion pipeline.
3.  **Develop the Scoring AI Prompt:** Write the system prompts to evaluate the news and assign the "Buy/Sell" weight.
4.  **UI Scaffolding:** Build the gauge indicator and the news feed layout with mock data to test the UX.
