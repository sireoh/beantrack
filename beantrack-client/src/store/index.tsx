import { create } from "zustand";
import { createNavbarSlice, NavbarState } from "./slices/navbar-slice";
import { createSearchSlice, SearchState } from "./slices/search-slice";
import {
  createWatchlistsSlice,
  WatchlistsState,
} from "./slices/watchlist-slice";
import { createSessionSlice, SessionState } from "./slices/session-slice";

export type StoreState = {
  navbar: NavbarState;
  search: SearchState;
  watchlists: WatchlistsState;
  session: SessionState;
};

export const useStore = create<StoreState>()((...a) => ({
  ...createNavbarSlice(...a),
  ...createSearchSlice(...a),
  ...createWatchlistsSlice(...a),
  ...createSessionSlice(...a),
}));
