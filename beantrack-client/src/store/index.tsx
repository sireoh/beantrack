import { create } from "zustand";
import { createNavbarSlice, NavbarState } from "./slices/navbar-slice";
import { createSearchSlice, SearchState } from "./slices/search-slice";

export type StoreState = {
  navbar: NavbarState;
  search: SearchState;
};

export const useStore = create<StoreState>()((...a) => ({
  ...createNavbarSlice(...a),
  ...createSearchSlice(...a),
}));
