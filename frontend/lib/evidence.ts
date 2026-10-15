import type { Evidence, Score } from "@/lib/api";

/** One slice of the student's text, with the scores whose evidence covers it. */
export type Segment = { start: number; end: number; text: string; scoreIds: string[] };

/**
 * The document a segmentation offset indexes. The API joins the two segments with a newline, and the
 * combined document is the analysis alone when there is no AI output
 * (backend/app/routers/ingest.py, `PATCH /submissions/{id}/segmentation`). A space here would make
 * every offset on the boundary editor one character off.
 */
export const combinedDocument = (aiOutput: string, analysis: string): string =>
  aiOutput ? `${aiOutput}\n${analysis}` : analysis;

/**
 * The reading pane slices the text at the stored offsets instead of searching for the quote: a quote
 * can repeat in a document, and only the offsets say which occurrence the score actually cites.
 * Adjacent or overlapping spans are merged into one highlight so a sentence is not split in two.
 */
export function buildSegments(text: string, scores: Score[]): Segment[] {
  const spans = scores
    .flatMap((score) =>
      score.evidence.map((evidence: Evidence) => ({
        scoreId: score.id,
        start: evidence.start_offset,
        end: evidence.end_offset,
      })),
    )
    .filter((span) => span.start >= 0 && span.end > span.start && span.end <= text.length)
    .sort((a, b) => a.start - b.start || a.end - b.end);

  const segments: Segment[] = [];
  let cursor = 0;

  for (const span of spans) {
    // Offsets are half-open over the text the scores were computed on; clamp them to this render
    // so one stale offset cannot blank the whole pane.
    const start = Math.max(cursor, span.start);
    if (span.end <= start) continue;

    if (start > cursor) {
      segments.push({ start: cursor, end: start, text: text.slice(cursor, start), scoreIds: [] });
    }

    const last = segments[segments.length - 1];
    if (last?.scoreIds.length && last.end === start) {
      last.end = span.end;
      last.text = text.slice(last.start, span.end);
      last.scoreIds.push(span.scoreId);
    } else {
      segments.push({ start, end: span.end, text: text.slice(start, span.end), scoreIds: [span.scoreId] });
    }
    cursor = span.end;
  }

  if (cursor < text.length) {
    segments.push({ start: cursor, end: text.length, text: text.slice(cursor), scoreIds: [] });
  }
  return segments;
}
