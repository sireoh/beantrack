import { WatchlistItem } from "@/models";
import { Dispatch, SetStateAction } from "react";

export async function fetchWatchlist(
  type: string,
  setWatchlist: Dispatch<SetStateAction<WatchlistItem[]>>,
  status: string | undefined
) {
  return type === "tv"
    ? fetchTVList(setWatchlist, status)
    : fetchMovielist(setWatchlist, status);
}

async function fetchTVList(
  setWatchlist: Dispatch<SetStateAction<WatchlistItem[]>>,
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
    setWatchlist(data.watchlist || []);
  } catch (err) {
    console.error("Error fetching watchlist:", err);
  }
}

async function fetchMovielist(
  setWatchlist: Dispatch<SetStateAction<WatchlistItem[]>>,
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
    console.log("Fetched watchlist:", data.watchlist || []);
    setWatchlist(data.watchlist || []);
  } catch (err) {
    console.error("Error fetching watchlist:", err);
  }
}
