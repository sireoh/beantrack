"use client";

import { useSearchParams } from "next/navigation";
import { useStore } from "@/store";
import { searchTVShow } from "@/hooks/search-tv-show";
import { searchMovies } from "@/hooks/search-movies";
import { MoviesResultsGrid } from "@/components/app/search/result-grids/movies-results-grid";
import { TVMazeResultEntryModel } from "@/models";
import { TVShowsResultsGrid } from "@/components/app/search/result-grids/tv-shows-results-grid";

export default function Home() {
  const searchParams = useSearchParams();
  const query = searchParams.get("q") ?? "";
  const search = useStore((state) => state.search);

  const {
    results: resultsTVShow,
    error: errorTVShow,
    loading: loadingTVShow,
  } = searchTVShow(query);

  const {
    results: resultsMovies,
    error: errorMovies,
    loading: loadingMovies,
  } = searchMovies(query);

  if (errorTVShow && errorMovies) {
    return (
      <p>
        Error: {errorTVShow} / {errorMovies}
      </p>
    );
  }

  if (loadingTVShow && loadingMovies) {
    return <p>Loading...</p>;
  }

  return (
    <div className="col-lg-8 col-md-8">
      <div className="m-t nav-active-border b-primary grid lg:grid-cols-2 gap-4">
        {search.currentType === "tv" ? (
          (resultsTVShow as TVMazeResultEntryModel[]).length > 0 ? (
            <TVShowsResultsGrid results={resultsTVShow} />
          ) : (
            "No TV Shows Found."
          )
        ) : resultsMovies?.Response === "True" ? (
          <MoviesResultsGrid results={resultsMovies} />
        ) : (
          "No Movies Found."
        )}
      </div>
    </div>
  );
}
