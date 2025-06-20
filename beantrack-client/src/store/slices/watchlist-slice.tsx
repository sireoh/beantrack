import { StateCreator } from "zustand";

export interface WatchlistsState {
  tvlist: any[];
  movieslist: any[];
  updateTVList: (tvlist: any[]) => void;
  updateMoviesList: (movieslist: any[]) => void;
}

export const createWatchlistsSlice: StateCreator<{
  watchlists: WatchlistsState;
}> = (set) => ({
  watchlists: {
    tvlist: [],
    movieslist: [],

    updateTVList: (tvlist: any[]) => {
      set((state) => ({
        watchlists: {
          ...state.watchlists,
          tvlist,
        },
      }));
    },

    updateMoviesList: (movieslist: any[]) => {
      set((state) => ({
        watchlists: {
          ...state.watchlists,
          movieslist,
        },
      }));
    },
  },
});
