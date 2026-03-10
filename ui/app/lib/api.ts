/**
 * API Client
 * ==========
 * Centralized fetch functions for the Oil Intelligence Index API.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface IndexData {
    score: number;
    label: string;
    event_count: number;
    updated_at: string | null;
}

export interface IntelEvent {
    id: string;
    headline: string;
    source: string;
    source_url: string | null;
    relevance_score: number;
    signal_direction: number;
    signal_label: "bullish" | "bearish" | "neutral";
    ai_reasoning: string | null;
    event_time: string | null;
    created_at: string;
}

export interface EventsResponse {
    events: IntelEvent[];
    total: number;
    limit: number;
    offset: number;
}

export async function fetchIndex(): Promise<IndexData> {
    const res = await fetch(`${API_BASE}/api/v1/index`, {
        cache: "no-store",
    });
    if (!res.ok) throw new Error("Failed to fetch index");
    return res.json();
}

export async function fetchEvents(
    limit = 30,
    offset = 0,
    minRelevance = 1,
    sort: "recent" | "relevance" = "recent",
    days = 7
): Promise<EventsResponse> {
    const params = new URLSearchParams({
        limit: String(limit),
        offset: String(offset),
        min_relevance: String(minRelevance),
        sort,
        days: String(days),
    });
    const res = await fetch(`${API_BASE}/api/v1/events?${params}`, {
        cache: "no-store",
    });
    if (!res.ok) throw new Error("Failed to fetch events");
    return res.json();
}
