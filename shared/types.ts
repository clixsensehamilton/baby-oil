/**
 * Oil Intelligence Index — Shared Types
 * ======================================
 * Types shared between the UI (Next.js) and API responses.
 */

// ---- Index ----

export type IndexLabel =
    | "Strong Sell"
    | "Sell"
    | "Neutral"
    | "Buy"
    | "Strong Buy";

export interface IndexData {
    score: number;       // 0-100
    label: IndexLabel;
    updated_at: string;  // ISO 8601
}

export interface IndexHistoryPoint {
    score: number;
    label: IndexLabel;
    created_at: string;
}

// ---- Events ----

export type SignalLabel = "bullish" | "bearish" | "neutral";

export interface IntelEvent {
    id: string;
    headline: string;
    source: string;
    source_url: string | null;
    relevance_score: number;      // 1-10
    signal_direction: number;     // -1.0 to +1.0
    signal_label: SignalLabel;
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

// ---- Thresholds ----

export const INDEX_THRESHOLDS = {
    STRONG_SELL: { min: 0, max: 30 },
    SELL: { min: 31, max: 45 },
    NEUTRAL: { min: 46, max: 55 },
    BUY: { min: 56, max: 70 },
    STRONG_BUY: { min: 71, max: 100 },
} as const;

export const INDEX_COLORS: Record<IndexLabel, string> = {
    "Strong Sell": "#dc2626",
    Sell: "#f97316",
    Neutral: "#eab308",
    Buy: "#22c55e",
    "Strong Buy": "#16a34a",
};
