"use client";

import { useSearchParams } from "next/navigation";
import { useStore } from "@/store";
import { searchTVShow } from "@/hooks/search-tv-show";
import { searchMovies } from "@/hooks/search-movies";
import { MoviesResultsGrid } from "@/components/app/search/result-grids/movies-results-grid";
import { TVMazeResultEntryModel } from "@/models";
import { TVShowsResultsGrid } from "@/components/app/search/result-grids/tv-shows-results-grid";
import { useEffect } from "react";
import { fetchWatchlist } from "@/utils/fetch-watchlist";

export default function Home() {
  const searchParams = useSearchParams();
  const query = searchParams.get("q") ?? "";
  const search = useStore((state) => state.search);
  const { tvlist, movieslist, updateTVList, updateMoviesList } = useStore(
    (state) => state.watchlists
  );
  useEffect(() => {
    fetchWatchlist(
      search.currentType,
      updateTVList,
      updateMoviesList,
      undefined
    );
  }, []);

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

  // Filter out already added items
  let filteredTVShowResults: TVMazeResultEntryModel[] = [];
  let filteredMoviesResults = resultsMovies;

  if (search.currentType === "tv") {
    filteredTVShowResults = resultsTVShow
      .filter(
        (item) =>
          item.show.externals?.imdb !== null &&
          item.show.externals?.imdb !== undefined &&
          item.show.externals?.imdb.trim() !== ""
      )
      .map((item) => ({
        ...item,
        show: {
          ...item.show,
          isAdded: tvlist.some((tv) => tv.imdb === item.show.externals?.imdb),
        },
      }));
  } else if (
    search.currentType === "movies" &&
    resultsMovies?.Response === "True"
  ) {
    filteredMoviesResults = {
      ...resultsMovies,
      Search: resultsMovies.Search?.map((item) => ({
        ...item,
        isAdded: movieslist.some((movie) => movie.imdb === item.imdbID),
      })),
    };
  }

  return (
    <div className="col-lg-8 col-md-8">
      <div className="m-t nav-active-border b-primary grid lg:grid-cols-2 gap-4">
        {search.currentType === "tv" ? (
          filteredTVShowResults.length > 0 ? (
            <TVShowsResultsGrid results={filteredTVShowResults} />
          ) : (
            "No TV Shows Found."
          )
        ) : filteredMoviesResults?.Response === "True" ? (
          <MoviesResultsGrid results={filteredMoviesResults} />
        ) : (
          "No Movies Found."
        )}
      </div>
    </div>
  );
}
