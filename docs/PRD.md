# Product Requirements Document (PRD): Oil Intelligence Index

## 1. Project Vision
The Oil Intelligence Index is a real-time data aggregation and analysis dashboard designed to predict short-term oil price movements ("Buy" or "Sell" signals). Unlike traditional sentiment indices (which rely on delayed financial news or trader mood), this index is grounded in **Open-Source Intelligence (OSINT)**—specifically, raw data on geopolitical conflicts, physical supply chain disruptions, and global logistics anomalies.

## 2. Target Audience
*   Commodity Traders (Oil, LNG).
*   Geopolitical Risk Analysts.
*   Energy Sector Executives.

## 3. Core Problems to Solve
*   **The "Priced-In" Problem:** Mainstream news (Bloomberg, Reuters) is often delayed; by the time it reports a pipeline attack, the market has already reacted.
*   **Information Overload:** Traders struggle to filter signal from noise across Telegram, specialized Twitter feeds, and raw satellite data.

## 4. Key Features & Requirements

### 4.1. The "Buy/Sell" Indicator (The Hero Metric)
*   **Requirement:** A centralized gauge (0-100 scale) indicating current market pressure.
*   **Logic:** 
    *   `0-30`: Strong Sell (Oversupply, de-escalation of conflicts, SPR releases).
    *   `31-45`: Sell.
    *   `46-55`: Neutral.
    *   `56-70`: Buy.
    *   `71-100`: Strong Buy (Major supply disruptions, imminent war in oil regions, critical infrastructure attacks).
*   **Update Frequency:** Real-time (or near real-time, matching ingestion intervals).

### 4.2. The OSINT Data Ingestion Pipeline
*   **Requirement:** Automated scraping and API ingestion from primary sources.
*   **Target Sources:**
    *   **Geopolitics:** ACLED (Armed Conflict Location Data), Local Telegram channels (Middle East/Eastern Europe conflict monitors).
    *   **Infrastructure:** NASA FIRMS (thermal anomalies/explosions at refineries).
    *   **Logistics:** AIS vessel tracking APIs (bottlenecks at Strait of Hormuz, Suez, etc.), Specialized shadow-fleet trackers.

### 4.3. The AI Evaluation Engine (NLP)
*   **Requirement:** Every ingested data point must be parsed by an LLM.
*   **Tasks:**
    1.  **Verification:** Is the event credible?
    2.  **Relevance Score (1-10):** How massive is the impact on global supply? (e.g., Houthis attacking a tanker = 8, a politician making a speech = 2).
    3.  **Signal Direction (-1/Bearish to +1/Bullish):** Does this event raise or lower oil prices?

### 4.4. The Intelligence Feed (Dashboard UI)
*   **Requirement:** A scrolling UI feed below the main indicator showing the *"Why"* behind the current score.
*   **Data Displayed per Item:** Raw headline/image, AI Relevance Score, Bullish/Bearish tag, and a link to the original raw source.

## 5. Non-Functional Requirements
*   **Architecture:** Web-based dashboard (React/Next.js) with a robust backend (Node/Python) handling the heavy Cron-based scraping and AI API calls.
*   **Performance:** The UI must load instantly. The heavy lifting (AI processing) must be done asynchronously on the backend before being pushed to the frontend database.
*   **Scalability:** The ingestion pipeline must be modular so new OSINT sources (e.g., a new relevant Telegram channel) can be added with just a configuration change.
