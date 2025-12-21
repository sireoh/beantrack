import { WatchlistItem } from "@/models";

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
    const url = status ? `/api/tvlist/${status}` : "/api/tvlist";
    const res = await fetch(url, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });

    if (!res.ok) {
      console.error("Failed to fetch TV show list");
      return;
    }

    const data = await res.json();
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
    const url = status ? `/api/movielist/${status}` : "/api/movielist";
    const res = await fetch(url, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });

    if (!res.ok) {
      console.error("Failed to fetch Movie list");
      return;
    }

    const data = await res.json();
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
