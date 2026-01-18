/**
 * Global Error Page
 */
"use client";

import { ErrorDisplay } from "@/components/ui/error-boundary";

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    return (
        <html>
            <body>
                <ErrorDisplay error={error} reset={reset} />
            </body>
        </html>
    );
}
