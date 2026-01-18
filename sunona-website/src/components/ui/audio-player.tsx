/**
 * Audio Player Component
 * For playing call recordings with waveform
 */
"use client";

import * as React from "react";
import { Play, Pause, RotateCcw, Download, Volume2, VolumeX } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface AudioPlayerProps {
    src?: string;
    title?: string;
    duration?: number;
    onDownload?: () => void;
    className?: string;
}

export function AudioPlayer({
    src,
    title = "Recording",
    duration = 0,
    onDownload,
    className,
}: AudioPlayerProps) {
    const [isPlaying, setIsPlaying] = React.useState(false);
    const [currentTime, setCurrentTime] = React.useState(0);
    const [isMuted, setIsMuted] = React.useState(false);
    const audioRef = React.useRef<HTMLAudioElement>(null);

    const totalDuration = duration || 180; // Default 3 min for demo

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, "0")}`;
    };

    const handlePlayPause = () => {
        if (audioRef.current) {
            if (isPlaying) {
                audioRef.current.pause();
            } else {
                audioRef.current.play();
            }
        }
        setIsPlaying(!isPlaying);
    };

    const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        const newTime = percent * totalDuration;
        setCurrentTime(newTime);
        if (audioRef.current) {
            audioRef.current.currentTime = newTime;
        }
    };

    const handleReset = () => {
        setCurrentTime(0);
        setIsPlaying(false);
        if (audioRef.current) {
            audioRef.current.currentTime = 0;
            audioRef.current.pause();
        }
    };

    const progress = (currentTime / totalDuration) * 100;

    // Generate fake waveform data
    const waveformBars = React.useMemo(() => {
        return Array.from({ length: 50 }, () => Math.random() * 0.7 + 0.3);
    }, []);

    return (
        <div className={cn("bg-[#1A1A2E] rounded-xl p-4 border border-[#374151]", className)}>
            {src && <audio ref={audioRef} src={src} />}

            {/* Title */}
            <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-medium text-white">{title}</span>
                <span className="text-xs text-gray-500">
                    {formatTime(currentTime)} / {formatTime(totalDuration)}
                </span>
            </div>

            {/* Waveform */}
            <div
                className="relative h-16 flex items-center gap-0.5 cursor-pointer mb-4"
                onClick={handleSeek}
            >
                {waveformBars.map((height, i) => {
                    const barProgress = (i / waveformBars.length) * 100;
                    const isPast = barProgress < progress;
                    return (
                        <div
                            key={i}
                            className={cn(
                                "flex-1 rounded-full transition-colors",
                                isPast ? "bg-purple-500" : "bg-[#374151]"
                            )}
                            style={{ height: `${height * 100}%` }}
                        />
                    );
                })}
                {/* Progress indicator */}
                <div
                    className="absolute top-0 bottom-0 w-0.5 bg-white"
                    style={{ left: `${progress}%` }}
                />
            </div>

            {/* Controls */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={handleReset}
                        className="h-9 w-9"
                    >
                        <RotateCcw className="h-4 w-4" />
                    </Button>
                    <Button
                        variant="primary"
                        size="icon"
                        onClick={handlePlayPause}
                        className="h-10 w-10"
                    >
                        {isPlaying ? (
                            <Pause className="h-5 w-5" />
                        ) : (
                            <Play className="h-5 w-5 ml-0.5" />
                        )}
                    </Button>
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setIsMuted(!isMuted)}
                        className="h-9 w-9"
                    >
                        {isMuted ? (
                            <VolumeX className="h-4 w-4" />
                        ) : (
                            <Volume2 className="h-4 w-4" />
                        )}
                    </Button>
                </div>

                {onDownload && (
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={onDownload}
                        leftIcon={<Download className="h-4 w-4" />}
                    >
                        Download
                    </Button>
                )}
            </div>
        </div>
    );
}

/**
 * Transcript Display Component
 */
interface TranscriptEntry {
    speaker: "agent" | "user";
    text: string;
    timestamp: number;
}

interface TranscriptProps {
    entries: TranscriptEntry[];
    currentTime?: number;
    className?: string;
}

export function Transcript({ entries, currentTime = 0, className }: TranscriptProps) {
    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, "0")}`;
    };

    return (
        <div className={cn("space-y-3 max-h-80 overflow-y-auto", className)}>
            {entries.map((entry, i) => (
                <div
                    key={i}
                    className={cn(
                        "flex gap-3 p-3 rounded-lg transition-colors",
                        entry.timestamp <= currentTime ? "bg-[#252540]" : "bg-[#1A1A2E]"
                    )}
                >
                    <div className="shrink-0">
                        <div
                            className={cn(
                                "w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium",
                                entry.speaker === "agent"
                                    ? "bg-purple-500/20 text-purple-400"
                                    : "bg-blue-500/20 text-blue-400"
                            )}
                        >
                            {entry.speaker === "agent" ? "AI" : "U"}
                        </div>
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium text-gray-400 capitalize">
                                {entry.speaker === "agent" ? "Agent" : "User"}
                            </span>
                            <span className="text-xs text-gray-600">
                                {formatTime(entry.timestamp)}
                            </span>
                        </div>
                        <p className="text-sm text-gray-300">{entry.text}</p>
                    </div>
                </div>
            ))}
        </div>
    );
}
