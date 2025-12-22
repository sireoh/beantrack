import { useEffect, useState } from "react";
import { SearchResult, TVMazeResults } from "@/models";
import { searchTVShows } from "@/api/api";

export function useSearchTVShow(query: string): SearchResult<TVMazeResults> {
  const [results, setResults] = useState<TVMazeResults>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query) return;

    async function fetchTVShows() {
      setLoading(true);
      setError(null);
      try {
        const data = await searchTVShows(query);
        setResults(data.results || []);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Unknown error");
        setResults([]);
      } finally {
        setLoading(false);
      }
    }

    fetchTVShows();
  }, [query]);

  return { results, error, loading };
}
