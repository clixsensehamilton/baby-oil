# Intelligence Network: Research & Data Sources

Based on the goal of building a real-time Oil Intelligence Index (a "Buy/Sell" indicator based on OSINT), here is a curated list of data sources we can use to build our aggregation and scoring engine.

## 1. High-Value OSINT Data Sources (Non-Delayed Intelligence)

To build an accurate indicator, we need data directly from primary and specialized sources before they hit mainstream financial news:

### A. Conflict & Geopolitical Event Data (High Relevance / Fast Signal)
*   **[ACLED (Armed Conflict Location & Event Data Project)](https://acleddata.com/)**: Essential for tracking political violence and conflicts worldwide. The API can provide real-time event updates.
*   **Telegram & Local OSINT**: Raw feeds from military bloggers and local news channels in key oil-producing regions (e.g., Middle East, Eastern Europe). This requires a custom MTProto scraper.

### B. Maritime & Oil Supply Tracking (Core Supply Metrics)
*   **AIS (Automatic Identification System) Data APIs**: Essential for monitoring tanker movements, discovering "dark fleets" (vessels turning off trackers), and tracking delays at major logistical chokepoints like the Strait of Hormuz.
*   **Specialized Twitter/X Trackers**: Accounts like `@RUTankerTracker` provide automated or highly curated lists of oil and gas tankers leaving specific ports.

### C. Physical Infrastructure Anomalies
*   **[NASA FIRMS (Fire Information for Resource Management System)](https://firms.modaps.eosdis.nasa.gov/)**: Provides near real-time satellite thermal anomaly detection. Crucial for detecting unauthorized explosions at oil refineries or pipelines globally before official announcements.

## 2. Architecural Inspiration (Index & Aggregator Repos)

While we are not building a 3D globe, we can look at data aggregation methodologies from existing OSINT projects:
*   **Threat Intelligence Aggregators (e.g., Valyu API)**: Examining how they synthesize conflict reports and assign threat levels can inform our AI scoring algorithm.
*   **Financial Sentiment Indices**: The architecture of tools like the Crypto "Fear and Greed Index" (how they weight different data inputs over time) is the structural model we need to replicate and apply to the oil OSINT dataset.

### A. Conflict & Geopolitical Event Data
*   **[ACLED (Armed Conflict Location & Event Data Project)](https://acleddata.com/)**: The gold standard for real-time data on political violence, protests, and conflicts worldwide.
*   **[GDELT Project](https://www.gdeltproject.org/)**: Monitors the world's broadcast, print, and web news in over 100 languages in real-time.
*   **Valyu API**: Used by some threat maps to synthesize conflict intelligence and military base information.

### B. Maritime & Oil Supply Tracking (Crucial for Oil Prices)
Since we are tracking oil conflicts, maritime tracking of oil tankers and shadow fleets is vital:
*   **AIS (Automatic Identification System) Data APIs**: Tracks vessel movements globally. Look for sudden destination changes or vessels turning off AIS ("dark ships").
*   **Twitter/X Bots (e.g., @RUTankerTracker)**: Specialized bots that automatically track oil and gas tankers leaving specific high-conflict ports.
*   **Satellite Imagery Analysts (OSINT Communities)**: Monitoring transshipment hubs for illegal oil trades.

### C. Physical Infrastructure Alerts
*   **[NASA FIRMS (Fire Information for Resource Management System)](https://firms.modaps.eosdis.nasa.gov/)**: Provides near real-time satellite imagery. OSINT analysts use this to detect explosions at oil refineries, pipelines, or military bases *before* the news reports it.
*   **ADS-B Flight Tracking (e.g., Flightradar24 APIs, OpenSky Network)**: Tracking military aircraft movements, VIP jets, or sudden commercial airspace closures (indicating impending conflict).

### D. Primary Social Intelligence
*   **Telegram Channels**: Local news channels, military blogger channels, and raw combat footage feeds often report events hours before mainstream media. 
*   **Twitter/X OSINT Lists**: Curated lists of reliable OSINT accounts that verify footage and translate local reports.

## Proposed Tech Stack moving forward:
*   **Frontend**: Next.js with `globe.gl` / `Three.js` (for the 3D globe) or `Mapbox GL JS` (for flat strategic maps).
*   **Backend / Ingestion**: Node.js or Python backend to scrape Telegram, ingest ACLED/GDELT APIs, and process AIS/ADS-B streams.
*   **AI Layer**: DeepSeek / OpenAI to quickly parse raw Telegram/Twitter feeds, verify locations, and translate them into structured JSON events to plot on the globe.
