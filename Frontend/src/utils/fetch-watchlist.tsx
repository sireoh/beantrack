import { WatchlistItem } from "@/models";
import { getUserTVList, getUserMovieList } from "@/api/api";

const sortOrder = {
  watching: 0,
  completed: 1,
  on_hold: 2,
  dropped: 3,
  plan_to_watch: 4,
};

export async function fetchWatchlist(
  type: string,
  updateTVList: (tvlist: WatchlistItem[]) => void,
  updateMoviesList: (movieslist: WatchlistItem[]) => void,
  status: string | undefined
) {
  return type === "tv"
    ? fetchTVList(updateTVList, status)
    : fetchMovielist(updateMoviesList, status);
}

async function fetchTVList(
  updateTVList: (tvlist: WatchlistItem[]) => void,
  status: string | undefined
) {
  try {
    const data = await getUserTVList(status);

    console.log("Fetched tvlist:", data.watchlist || []);

    // Sort the movielist by status
    if (!status) {
      data.watchlist.sort((a: WatchlistItem, b: WatchlistItem) => {
        return (
          (sortOrder[a.status as keyof typeof sortOrder] ?? 999) -
          (sortOrder[b.status as keyof typeof sortOrder] ?? 999)
        );
      });
    }

    updateTVList(data.watchlist || []);
  } catch (err) {
    console.error("Error fetching tvlist:", err);
  }
}

async function fetchMovielist(
  updateMoviesList: (movieslist: WatchlistItem[]) => void,
  status: string | undefined
) {
  try {
    const data = await getUserMovieList(status);

    console.log("Fetched movielist:", data.watchlist || []);

    // Sort the movielist by status
    if (!status) {
      data.watchlist.sort((a: WatchlistItem, b: WatchlistItem) => {
        return (
          (sortOrder[a.status as keyof typeof sortOrder] ?? 999) -
          (sortOrder[b.status as keyof typeof sortOrder] ?? 999)
        );
      });
    }

    updateMoviesList(data.watchlist || []);
  } catch (err) {
    console.error("Error fetching movielist:", err);
  }
}
