import { WatchlistItem } from "@/models";
import { StateCreator } from "zustand";

export interface WatchlistsState {
  tvlist: WatchlistItem[];
  movieslist: WatchlistItem[];
  updateTVList: (tvlist: WatchlistItem[]) => void;
  updateMoviesList: (movieslist: WatchlistItem[]) => void;
}

export const createWatchlistsSlice: StateCreator<{
  watchlists: WatchlistsState;
}> = (set) => ({
  watchlists: {
    tvlist: [],
    movieslist: [],

    updateTVList: (tvlist: WatchlistItem[]) => {
      set((state) => ({
        watchlists: {
          ...state.watchlists,
          tvlist,
        },
      }));
    },

    updateMoviesList: (movieslist: WatchlistItem[]) => {
      set((state) => ({
        watchlists: {
          ...state.watchlists,
          movieslist,
        },
      }));
    },
  },
});
