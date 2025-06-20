import { create } from "zustand";
import { createNavbarSlice, NavbarState } from "./slices/navbar-slice";
import { createSearchSlice, SearchState } from "./slices/search-slice";
import {
  createWatchlistsSlice,
  WatchlistsState,
} from "./slices/watchlist-slice";

export type StoreState = {
  navbar: NavbarState;
  search: SearchState;
  watchlists: WatchlistsState;
};

export const useStore = create<StoreState>()((...a) => ({
  ...createNavbarSlice(...a),
  ...createSearchSlice(...a),
  ...createWatchlistsSlice(...a),
}));
