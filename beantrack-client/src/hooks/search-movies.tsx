import { OMDBResults, SearchResult } from "@/models";
import { useEffect, useState } from "react";

const OMDB_API_KEY = process.env.NEXT_PUBLIC_OMDB_API_KEY;
let MOVIES_API_ENDPOINT = process.env.NEXT_PUBLIC_MOVIES_API_ENDPOINT;

// Simple safety check and URL construction
MOVIES_API_ENDPOINT =
  OMDB_API_KEY && MOVIES_API_ENDPOINT
    ? MOVIES_API_ENDPOINT.replace("{%s}", OMDB_API_KEY)
    : "";

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

    const fetchData = async () => {
      setLoading(true);
      try {
        const url = `${MOVIES_API_ENDPOINT}${encodeURIComponent(query)}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error("Failed to fetch movies");
        const data = await res.json();

        setResults(__removeDuplicates(data));
        setError(null);
      } catch (err: any) {
        setError(err.message);
        setResults({
          Search: [],
          totalResults: "0",
          Response: "",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
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
