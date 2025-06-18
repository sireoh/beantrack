import { SearchResult, TVMazeResults } from "@/models";
import { useEffect, useState } from "react";

const TV_SHOW_API_ENDPOINT = process.env.NEXT_PUBLIC_TV_SHOW_API_ENDPOINT;

export function searchTVShow(query: string): SearchResult<TVMazeResults> {
  const [results, setResults] = useState<TVMazeResults>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await fetch(
          `${TV_SHOW_API_ENDPOINT}${encodeURIComponent(query)}`
        );
        if (!res.ok) throw new Error("Failed to fetch shows");
        const data = await res.json();
        setResults(data);
        setError(null);
      } catch (err: any) {
        setError(err.message);
        setResults([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [query]);

  return { results, error, loading };
}
