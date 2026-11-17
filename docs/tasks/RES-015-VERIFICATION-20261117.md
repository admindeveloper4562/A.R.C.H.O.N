# RES-015 Live-Source Verification

## Scope

- Parent: `RES-015`
- Baseline: `5156e39b417e71dbfe211ea738315ebc0da38cc4`
- Task mode: `audit`
- Observed: `2026-11-17T16:13:43Z`–`2026-11-17T16:13:49Z`
- Access: public HTTPS reads only; no credentials or private data were used

This record supplies the live-source prerequisite for independent QC. It does
not by itself mark the parent complete.

## Question and bounded answer

**Question:** Across a live web source and a public video source, what SQLite
operations are covered and what transaction behavior should the implementation
preserve?

**Answer:** The live YouTube description lists chapter-level coverage of
database initialization, table creation, insertion, querying, deletion and
update. The Python documentation independently describes `Connection` and
cursor execution, and documents connection-context-manager commit on success
and rollback on an exception. The sources support the same implementation
direction; the video evidence is chapter/description metadata rather than an
exact caption transcript.

## Source evidence

| Source ID | URI | Source date | Observation | Captured evidence SHA-256 |
| --- | --- | --- | --- | --- |
| `python_docs` | https://docs.python.org/3/library/sqlite3.html | not stated | 2026-11-17T16:13:43.984907Z | `580e225abce2780f6b8b7e9c6d7e573145a82248d4a64fb7eb7bf3733df28de8` |
| `youtube` | https://www.youtube.com/watch?v=tXJtY51xHq8 | 2024-11-28T06:01:00-08:00 | 2026-11-17T16:13:46.034177Z | `e0aa06c5cefa25addc100e880660a39b0d00f5d958b492a32be00e73ee977505` |
| `transcript_mirror` | https://videodb.org/python-sqlite-tutorial-complete-overview-creating-a-database-table-and-running-queries/pd-0G0MigUA | 2017-04-18 | 2026-11-17T16:13:46.803282Z | `58d5f4c06a22f8d9c2a9e858a5f3936231c294d9c7446745584ba7e91dee9ada` |

The transcript mirror is retained as secondary corroboration only; it is not
treated as authoritative YouTube timing evidence.

## Timestamped video evidence

The YouTube page exposes these chapter start links in its public description:

| Chapter | Start | Timestamped source |
| --- | ---: | --- |
| Initialize a SQLite Database | 06:05 | https://www.youtube.com/watch?v=tXJtY51xHq8&t=365s |
| Create a SQLite Table | 09:00 | https://www.youtube.com/watch?v=tXJtY51xHq8&t=540s |
| Insert data into a Database | 14:24 | https://www.youtube.com/watch?v=tXJtY51xHq8&t=864s |
| Query data in SQL | 22:20 | https://www.youtube.com/watch?v=tXJtY51xHq8&t=1340s |
| Delete data from a Database | 27:15 | https://www.youtube.com/watch?v=tXJtY51xHq8&t=1635s |
| Update existing data | 30:55 | https://www.youtube.com/watch?v=tXJtY51xHq8&t=1855s |

## Runtime exercise

The live fetch was executed through `WebDiscoveryService` with exact-host
HTTPS policies for `docs.python.org`, `www.youtube.com` and the explicitly
identified public transcript mirror. `YouTubeResearchService` persisted the
YouTube metadata observation and returned `partial` with
`transcript_unavailable`; the provider's timed-text endpoint returned an empty
response. No exact caption-segment offsets are claimed.

The existing deterministic research suite remains green:

```text
PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -p 'test_research_*.py' -q
Ran 57 tests in 0.467s
OK
```

## Limitations and QC boundary

- Chapter starts are precise links to the video description's published
  structure, not caption-level offsets.
- The transcript mirror is secondary and not used to manufacture offsets.
- The report contains no raw page, transcript, credentials or private data.
- Independent QC must verify the source links, digests, report claims and the
  acceptance interpretation before RES-015 can become `completed`.

## Decision

`READY_FOR_QC`: the previously missing permitted live-source evidence is
available and source-bound. Parent completion remains controlled by the
Master's normal candidate, independent-QC and serialized-Merger workflow.
