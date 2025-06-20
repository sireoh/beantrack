import { WatchlistsState } from "@/store/slices/watchlist-slice";

export async function hydrateWatchlists(watchlists: WatchlistsState) {
  try {
    const res = await fetch("/api/tv_show", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
    });

    if (!res.ok) throw new Error("Failed to fetch TV list");

    const data = await res.json();

    if (data.tvlist && Array.isArray(data.tvlist)) {
      watchlists.updateTVList(data.tvlist);
    } else {
      console.warn("Unexpected response:", data);
    }
  } catch (err) {
    console.error("Error hydrating watchlists:", err);
  }
}
