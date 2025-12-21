import { OMDBResults, SearchResult } from "@/models";
import { useEffect, useState } from "react";

export function searchMovies(query: string): SearchResult<OMDBResults> {
  const [results, setResults] = useState<OMDBResults>({
    Search: [],
    totalResults: "0",
    Response: "",
  });

  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query) return;

    const fetchMovies = async () => {
      setLoading(true);
      try {
        const res = await fetch(
          `/api/search/movie?q=${encodeURIComponent(query)}`,
          {
            method: "POST",
            credentials: "include", // optional depending on auth/cookies
          }
        );

        if (!res.ok)
          throw new Error(`Failed to fetch movies: ${res.statusText}`);
        const data = await res.json();

        setResults(
          __removeDuplicates(
            data.results || {
              Search: [],
              totalResults: "0",
              Response: "",
            }
          )
        );
        setError(null);
      } catch (err: any) {
        setError(err.message || "Unknown error");
        setResults({
          Search: [],
          totalResults: "0",
          Response: "",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, [query]);

  return { results, error, loading };
}

// Middleware-like helper to remove duplicates by imdbID
function __removeDuplicates(data: OMDBResults): OMDBResults {
  if (!data?.Search) return data;

  const uniqueMap = new Map<string, (typeof data.Search)[0]>();
  for (const item of data.Search) {
    uniqueMap.set(item.imdbID, item); // overwrite duplicates
  }

  return {
    ...data,
    Search: Array.from(uniqueMap.values()),
  };
}
