import { useEffect, useState } from "react";
import { SearchResult, TVMazeResults } from "@/models";

export function searchTVShow(query: string): SearchResult<TVMazeResults> {
  const [results, setResults] = useState<TVMazeResults>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query) return;

    async function fetchTVShows() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(
          `/api/search/tv_show?q=${encodeURIComponent(query)}`,
          {
            method: "POST",
            credentials: "include", // optional, remove if not using cookies/auth
          }
        );

        if (!res.ok) {
          throw new Error(`Error: ${res.status}`);
        }

        const data = await res.json();
        setResults(data.results || []);
      } catch (err: any) {
        setError(err.message || "Unknown error");
        setResults([]);
      } finally {
        setLoading(false);
      }
    }

    fetchTVShows();
  }, [query]);

  return { results, error, loading };
}
