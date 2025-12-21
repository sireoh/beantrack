import { WatchlistItem } from "@/models";
import { StateCreator } from "zustand";

export interface WatchlistsState {
  tvlist: WatchlistItem[];
  movieslist: WatchlistItem[];
  updateTVList: (tvlist: WatchlistItem[]) => void;
  updateMoviesList: (movieslist: WatchlistItem[]) => void;
  deleteTVListItem: (imdb: string) => void;
  deleteMovieListItem: (imdb: string) => void;
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

    deleteTVListItem: (imdb: string) => {
      set((state) => ({
        watchlists: {
          ...state.watchlists,
          tvlist: state.watchlists.tvlist.filter((item) => item.imdb !== imdb),
        },
      }));
    },

    deleteMovieListItem: (imdb: string) => {
      set((state) => ({
        watchlists: {
          ...state.watchlists,
          movieslist: state.watchlists.movieslist.filter(
            (item) => item.imdb !== imdb
          ),
        },
      }));
    },
  },
});
