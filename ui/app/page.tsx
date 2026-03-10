import GaugeIndicator from "./components/GaugeIndicator";
import EventFeed from "./components/EventFeed";
import { fetchIndex, fetchEvents, type IndexData, type EventsResponse } from "./lib/api";

// Mock data for initial development (used when API is not running)
const MOCK_INDEX: IndexData = {
  score: 62,
  label: "Buy",
  event_count: 14,
  updated_at: new Date().toISOString(),
};

const MOCK_EVENTS: EventsResponse = {
  events: [
    {
      id: "mock-1",
      headline: "Houthi forces claim attack on oil tanker near Strait of Hormuz",
      source: "Reuters Energy",
      source_url: "https://reuters.com",
      relevance_score: 9,
      signal_direction: 0.85,
      signal_label: "bullish" as const,
      ai_reasoning: "Direct attack on oil shipping lane — major supply disruption risk.",
      event_time: new Date(Date.now() - 3600000).toISOString(),
      created_at: new Date(Date.now() - 3600000).toISOString(),
    },
    {
      id: "mock-2",
      headline: "OPEC+ members signal potential production increase at next summit",
      source: "OilPrice.com",
      source_url: "https://oilprice.com",
      relevance_score: 7,
      signal_direction: -0.6,
      signal_label: "bearish" as const,
      ai_reasoning: "Production increase would add supply, pushing prices down.",
      event_time: new Date(Date.now() - 7200000).toISOString(),
      created_at: new Date(Date.now() - 7200000).toISOString(),
    },
    {
      id: "mock-3",
      headline: "US Strategic Petroleum Reserve drawdown paused amid rising tensions",
      source: "Reuters Energy",
      source_url: "https://reuters.com",
      relevance_score: 6,
      signal_direction: 0.4,
      signal_label: "bullish" as const,
      ai_reasoning: "Pausing SPR drawdown tightens supply slightly — moderately bullish.",
      event_time: new Date(Date.now() - 10800000).toISOString(),
      created_at: new Date(Date.now() - 10800000).toISOString(),
    },
    {
      id: "mock-4",
      headline: "Libya's eastern oil fields resume full production after ceasefire agreement",
      source: "ACLED Conflict",
      source_url: null,
      relevance_score: 8,
      signal_direction: -0.7,
      signal_label: "bearish" as const,
      ai_reasoning: "Resumption of Libyan production adds significant supply to market.",
      event_time: new Date(Date.now() - 14400000).toISOString(),
      created_at: new Date(Date.now() - 14400000).toISOString(),
    },
    {
      id: "mock-5",
      headline: "Satellite imagery shows abnormal thermal activity at Iraqi refinery complex",
      source: "NASA FIRMS",
      source_url: null,
      relevance_score: 5,
      signal_direction: 0.3,
      signal_label: "neutral" as const,
      ai_reasoning: "Thermal anomaly detected but not confirmed as attack. Monitoring.",
      event_time: new Date(Date.now() - 18000000).toISOString(),
      created_at: new Date(Date.now() - 18000000).toISOString(),
    },
  ],
  total: 5,
  limit: 20,
  offset: 0,
};

export default async function Home() {
  let indexData = MOCK_INDEX;
  let eventsData = MOCK_EVENTS;

  // Try to fetch real data from the API
  try {
    const [realIndex, realEvents] = await Promise.all([
      fetchIndex(),
      fetchEvents(20, 0, 1),
    ]);
    indexData = realIndex;
    eventsData = realEvents;
  } catch {
    // API not running — fall back to mock data
    console.log("[UI] API unavailable — using mock data for development.");
  }

  return (
    <main className="min-h-screen px-4 py-8 md:px-8 lg:px-16">
      {/* Top bar */}
      <header className="flex items-center justify-between mb-10">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-amber-500" />
          <h1 className="text-lg font-bold tracking-wide">
            OIL<span style={{ color: "var(--text-muted)" }}>INTEL</span>
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-xs" style={{ color: "var(--text-muted)" }}>
            LIVE
          </span>
        </div>
      </header>

      {/* Dashboard grid */}
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Gauge */}
        <GaugeIndicator
          score={indexData.score}
          label={indexData.label}
          eventCount={indexData.event_count}
          updatedAt={indexData.updated_at}
        />

        {/* Feed */}
        <EventFeed
          events={eventsData.events}
          total={eventsData.total}
        />
      </div>

      {/* Footer */}
      <footer
        className="text-center mt-12 text-xs"
        style={{ color: "var(--text-muted)" }}
      >
        Oil Intelligence Index — OSINT-powered market intelligence
      </footer>
    </main>
  );
}
