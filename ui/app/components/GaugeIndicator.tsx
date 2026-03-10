"use client";

import { useEffect, useRef } from "react";

interface GaugeIndicatorProps {
    score: number; // 0-100
    label: string;
    eventCount: number;
    updatedAt: string | null;
}

function getScoreColor(score: number): string {
    if (score <= 30) return "#ef4444";
    if (score <= 45) return "#f97316";
    if (score <= 55) return "#eab308";
    if (score <= 70) return "#22c55e";
    return "#16a34a";
}

function getGlowColor(score: number): string {
    if (score <= 30) return "rgba(239, 68, 68, 0.3)";
    if (score <= 45) return "rgba(249, 115, 22, 0.3)";
    if (score <= 55) return "rgba(234, 179, 8, 0.3)";
    if (score <= 70) return "rgba(34, 197, 94, 0.3)";
    return "rgba(22, 163, 74, 0.3)";
}

export default function GaugeIndicator({
    score,
    label,
    eventCount,
    updatedAt,
}: GaugeIndicatorProps) {
    const color = getScoreColor(score);
    const glow = getGlowColor(score);

    // SVG arc math
    const radius = 80;
    const circumference = Math.PI * radius; // semicircle
    const progress = (score / 100) * circumference;
    const dashOffset = circumference - progress;

    const formattedTime = updatedAt
        ? new Date(updatedAt).toLocaleTimeString("en-PH", {
            timeZone: "Asia/Manila",
            hour: "2-digit",
            minute: "2-digit",
            hour12: true,
        })
        : "—";

    return (
        <div className="glass-card p-8 flex flex-col items-center justify-center">
            {/* Header */}
            <div className="text-center mb-4">
                <h2
                    className="text-sm font-semibold tracking-[0.2em] uppercase"
                    style={{ color: "var(--text-muted)" }}
                >
                    Oil Intelligence Index
                </h2>
            </div>

            {/* Gauge SVG */}
            <div className="relative w-[220px] h-[130px] mb-2">
                <svg
                    viewBox="0 0 200 110"
                    className="w-full h-full"
                    style={{ filter: `drop-shadow(0 0 20px ${glow})` }}
                >
                    {/* Background arc */}
                    <path
                        d="M 20 100 A 80 80 0 0 1 180 100"
                        fill="none"
                        stroke="var(--border-color)"
                        strokeWidth="10"
                        strokeLinecap="round"
                    />
                    {/* Filled arc */}
                    <path
                        d="M 20 100 A 80 80 0 0 1 180 100"
                        fill="none"
                        stroke={color}
                        strokeWidth="10"
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        strokeDashoffset={dashOffset}
                        style={{
                            transition: "stroke-dashoffset 1.2s ease-out, stroke 0.6s ease",
                        }}
                    />
                </svg>

                {/* Score number */}
                <div className="absolute inset-0 flex flex-col items-center justify-end pb-1">
                    <span
                        className="text-5xl font-black tabular-nums"
                        style={{
                            color,
                            fontFamily: "var(--font-mono)",
                            textShadow: `0 0 30px ${glow}`,
                        }}
                    >
                        {score}
                    </span>
                </div>
            </div>

            {/* Label */}
            <div
                className="text-xl font-bold tracking-wide mb-4"
                style={{ color }}
            >
                {label.toUpperCase()}
            </div>

            {/* Scale labels */}
            <div className="flex justify-between w-full max-w-[240px] mb-6">
                <span className="text-xs font-medium" style={{ color: "#ef4444" }}>
                    STRONG SELL
                </span>
                <span className="text-xs font-medium" style={{ color: "#16a34a" }}>
                    STRONG BUY
                </span>
            </div>

            {/* Meta */}
            <div
                className="flex gap-6 text-xs"
                style={{ color: "var(--text-muted)" }}
            >
                <span>
                    <span className="font-semibold" style={{ color: "var(--text-secondary)" }}>
                        {eventCount}
                    </span>{" "}
                    events analyzed
                </span>
                <span>
                    Updated{" "}
                    <span className="font-semibold" style={{ color: "var(--text-secondary)" }}>
                        {formattedTime}
                    </span>
                </span>
            </div>
        </div>
    );
}
