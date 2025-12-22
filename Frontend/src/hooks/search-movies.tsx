import { OMDBResults, SearchResult } from "@/models";
import { useEffect, useState } from "react";
import { searchMovies as apiSearchMovies } from "@/api/api";

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
        const data = await apiSearchMovies(query);

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
