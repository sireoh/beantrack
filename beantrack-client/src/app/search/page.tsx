"use client";

import { useSearchParams } from "next/navigation";
import { useStore } from "@/store";
import { createTVShowResultsGrid, searchTVShow } from "@/hooks/search-tv-show";
import { searchMovies } from "@/hooks/search-movies";
import { MoviesResultsGrid } from "@/components/app/search/result-grids/movies-results-grid";
import { OMDBResults, TVMazeResultEntryModel, TVMazeResults } from "@/models";

export default function Home() {
  const searchParams = useSearchParams();
  const query = searchParams.get("q") ?? "";
  const search = useStore((state) => state.search);

  const { results, error, loading } =
    search.currentType === "tv" ? searchTVShow(query) : searchMovies(query);

  if (error) return <p>Error: {error}</p>;
  if (loading) return <p>Loading...</p>;

  return (
    <div className="col-lg-8 col-md-8">
      <div className="m-t nav-active-border b-primary grid lg:grid-cols-2 gap-4">
        {search.currentType === "tv" ? (
          (results as TVMazeResultEntryModel[]).length > 0 ? (
            createTVShowResultsGrid(results as TVMazeResults)
          ) : (
            "No TV Shows Found."
          )
        ) : (results as OMDBResults).Response === "True" ? (
          <MoviesResultsGrid results={results as OMDBResults} />
        ) : (
          "No Movies Found."
        )}
      </div>
    </div>
  );
}
