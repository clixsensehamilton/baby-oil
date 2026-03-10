"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { fetchEvents, type IntelEvent } from "../lib/api";

interface EventFeedProps {
    initialEvents: IntelEvent[];
    total: number;
}

function getSignalBadgeClass(label: string): string {
    switch (label) {
        case "bullish":
            return "badge-bullish";
        case "bearish":
            return "badge-bearish";
        default:
            return "badge-neutral";
    }
}

function getSignalIcon(label: string): string {
    switch (label) {
        case "bullish":
            return "▲";
        case "bearish":
            return "▼";
        default:
            return "●";
    }
}

function getRelevanceBar(score: number): string {
    const filled = score;
    const empty = 10 - score;
    return "█".repeat(filled) + "░".repeat(empty);
}

function formatTimeAgo(isoString: string): string {
    const diff = Date.now() - new Date(isoString).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "just now";
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
}

function formatManila(isoString: string): string {
    return new Date(isoString).toLocaleString("en-PH", {
        timeZone: "Asia/Manila",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
    });
}

const NASA_FIRMS_SOURCE = "NASA FIRMS";
const PAGE_SIZE = 20;

type SortMode = "recent" | "relevance";
type TabMode = "all" | "acled" | "eia" | "firms";

export default function EventFeed({ initialEvents, total: initialTotal }: EventFeedProps) {
    const [sortMode, setSortMode] = useState<SortMode>("recent");
    const [highImpactOnly, setHighImpactOnly] = useState(false);
    const [activeTab, setActiveTab] = useState<TabMode>("all");

    // Lazy-load state
    const [allEvents, setAllEvents] = useState<IntelEvent[]>(initialEvents);
    const [total, setTotal] = useState(initialTotal);
    const [loadingMore, setLoadingMore] = useState(false);
    const sentinelRef = useRef<HTMLDivElement>(null);

    const hasMore = allEvents.length < total;

    const loadMore = useCallback(async () => {
        if (loadingMore || !hasMore) return;
        setLoadingMore(true);
        try {
            const res = await fetchEvents(PAGE_SIZE, allEvents.length, 1, "recent", 30);
            setAllEvents((prev) => {
                const existingIds = new Set(prev.map((e) => e.id));
                const newEvents = res.events.filter((e) => !existingIds.has(e.id));
                return [...prev, ...newEvents];
            });
            setTotal(res.total);
        } catch {
            // silently fail — user can scroll again
        } finally {
            setLoadingMore(false);
        }
    }, [loadingMore, hasMore, allEvents.length]);

    useEffect(() => {
        const sentinel = sentinelRef.current;
        if (!sentinel) return;
        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting) loadMore();
            },
            { threshold: 0.1 }
        );
        observer.observe(sentinel);
        return () => observer.disconnect();
    }, [loadMore]);

    // Client-side filtering & sorting
    let filtered = allEvents;

    // 1. Filter by Tab
    if (activeTab === "firms") {
        filtered = filtered.filter((e) => e.source.includes(NASA_FIRMS_SOURCE));
    } else if (activeTab === "acled") {
        filtered = filtered.filter((e) => e.source.includes("ACLED"));
    } else if (activeTab === "eia") {
        filtered = filtered.filter((e) => e.source.includes("EIA"));
    } else {
        // "All" tab: show everything except NASA FIRMS (satellite noise)
        filtered = filtered.filter((e) => !e.source.includes(NASA_FIRMS_SOURCE));
    }

    // 2. Filter by Impact
    if (highImpactOnly) {
        filtered = filtered.filter((e) => e.relevance_score >= 7);
    }

    // 3. Sort
    if (sortMode === "relevance") {
        filtered = [...filtered].sort(
            (a, b) => b.relevance_score - a.relevance_score
        );
    }

    return (
        <div className="glass-card p-6">
            {/* Header row with Tabs */}
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <h2
                        className="text-sm font-semibold tracking-[0.15em] uppercase"
                        style={{ color: "var(--text-secondary)" }}
                    >
                        Intelligence Feed
                    </h2>
                </div>
                <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                    {total} total global events tracked
                </span>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-[var(--border-color)] mb-5 overflow-x-auto">
                {([
                    { key: "all" as TabMode, label: "All Intel" },
                    { key: "acled" as TabMode, label: "Conflict (ACLED)" },
                    { key: "eia" as TabMode, label: "EIA Data" },
                    { key: "firms" as TabMode, label: "Satellite (FIRMS)" },
                ]).map((tab) => (
                    <button
                        key={tab.key}
                        onClick={() => setActiveTab(tab.key)}
                        className={`px-4 py-2 text-sm font-medium transition-colors whitespace-nowrap ${activeTab === tab.key
                                ? "border-b-2 border-emerald-500 text-[var(--text-primary)]"
                                : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                            }`}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Controls */}
            <div className="flex items-center gap-3 mb-5">
                {/* Sort toggle */}
                <div
                    className="flex rounded-lg overflow-hidden text-xs"
                    style={{ border: "1px solid var(--border-color)" }}
                >
                    <button
                        onClick={() => setSortMode("recent")}
                        className="px-3 py-1.5 font-medium transition-colors duration-150"
                        style={{
                            background:
                                sortMode === "recent"
                                    ? "var(--bg-card-hover)"
                                    : "transparent",
                            color:
                                sortMode === "recent"
                                    ? "var(--text-primary)"
                                    : "var(--text-muted)",
                        }}
                    >
                        Most Recent
                    </button>
                    <button
                        onClick={() => setSortMode("relevance")}
                        className="px-3 py-1.5 font-medium transition-colors duration-150"
                        style={{
                            background:
                                sortMode === "relevance"
                                    ? "var(--bg-card-hover)"
                                    : "transparent",
                            color:
                                sortMode === "relevance"
                                    ? "var(--text-primary)"
                                    : "var(--text-muted)",
                        }}
                    >
                        Most Relevant
                    </button>
                </div>

                {/* High-impact filter */}
                <button
                    onClick={() => setHighImpactOnly(!highImpactOnly)}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors duration-150"
                    style={{
                        border: `1px solid ${highImpactOnly ? "#f97316" : "var(--border-color)"
                            }`,
                        background: highImpactOnly
                            ? "rgba(249, 115, 22, 0.15)"
                            : "transparent",
                        color: highImpactOnly ? "#f97316" : "var(--text-muted)",
                    }}
                >
                    ⚡ High Impact Only
                </button>

                {/* Count */}
                <span
                    className="text-xs ml-auto"
                    style={{ color: "var(--text-muted)" }}
                >
                    Showing {filtered.length} events
                </span>
            </div>

            {/* Event list */}
            {filtered.length === 0 ? (
                <div
                    className="py-16 text-center"
                    style={{ color: "var(--text-muted)" }}
                >
                    <p className="text-lg mb-2">
                        {highImpactOnly
                            ? "No high-impact events in this period"
                            : "No events processed yet"}
                    </p>
                    <p className="text-sm">
                        {highImpactOnly
                            ? "Try disabling the high-impact filter to see all events."
                            : "The pipeline will begin ingesting events on its next scrape cycle."}
                    </p>
                </div>
            ) : (
                <div className="space-y-3">
                    {filtered.map((event, idx) => (

                        <div
                            key={event.id}
                            className="feed-item p-4 rounded-xl transition-colors duration-200"
                            style={{
                                background: "var(--bg-card)",
                                borderLeft: `3px solid ${event.signal_label === "bullish"
                                    ? "#22c55e"
                                    : event.signal_label === "bearish"
                                        ? "#ef4444"
                                        : "#eab308"
                                    }`,
                                animationDelay: `${idx * 60}ms`,
                            }}
                            onMouseEnter={(e) =>
                                (e.currentTarget.style.background = "var(--bg-card-hover)")
                            }
                            onMouseLeave={(e) =>
                                (e.currentTarget.style.background = "var(--bg-card)")
                            }
                        >
                            {/* Top row: signal + headline */}
                            <div className="flex items-start gap-3 mb-2">
                                <span
                                    className={`${getSignalBadgeClass(
                                        event.signal_label
                                    )} px-2 py-0.5 rounded-md text-xs font-semibold shrink-0 mt-0.5`}
                                >
                                    {getSignalIcon(event.signal_label)}{" "}
                                    {event.signal_label.toUpperCase()}
                                </span>
                                <h3
                                    className="text-sm font-medium leading-snug"
                                    style={{ color: "var(--text-primary)" }}
                                >
                                    {event.headline}
                                </h3>
                            </div>

                            {/* AI Reasoning */}
                            {event.ai_reasoning && (
                                <p
                                    className="text-xs ml-[76px] mb-2 italic"
                                    style={{ color: "var(--text-muted)" }}
                                >
                                    {event.ai_reasoning}
                                </p>
                            )}

                            {/* Bottom row: meta */}
                            <div className="flex items-center gap-4 ml-[76px]">
                                <div
                                    className="flex items-center gap-2"
                                    title={`Relevance: ${event.relevance_score}/10`}
                                >
                                    <span
                                        className="text-xs font-mono"
                                        style={{ color: "var(--text-muted)" }}
                                    >
                                        {getRelevanceBar(event.relevance_score)}
                                    </span>
                                    <span
                                        className="text-xs font-bold"
                                        style={{ color: "var(--text-secondary)" }}
                                    >
                                        {event.relevance_score}/10
                                    </span>
                                </div>
                                <span
                                    className="text-xs"
                                    style={{ color: "var(--text-muted)" }}
                                >
                                    {event.source}
                                </span>
                                <span
                                    className="text-xs"
                                    style={{ color: "var(--text-muted)" }}
                                    title={formatManila(event.event_time || event.created_at)}
                                >
                                    {formatTimeAgo(event.event_time || event.created_at)} · {formatManila(event.event_time || event.created_at)}
                                </span>
                                {event.source_url && (
                                    <a
                                        href={event.source_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-xs underline hover:no-underline"
                                        style={{ color: "var(--text-muted)" }}
                                    >
                                        source →
                                    </a>
                                )}
                            </div>
                        </div>
                    ))}

                    {/* Lazy load sentinel */}
                    <div ref={sentinelRef} className="py-2 text-center">
                        {loadingMore && (
                            <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                                Loading more…
                            </span>
                        )}
                        {!hasMore && allEvents.length > PAGE_SIZE && (
                            <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                                — end of feed —
                            </span>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
