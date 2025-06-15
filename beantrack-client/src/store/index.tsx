import { create } from "zustand";
import { createNavbarSlice, NavbarState } from "./slices/navbar-slice";

export type StoreState = {
  navbar: NavbarState;
};

export const useStore = create<StoreState>()((...a) => ({
  ...createNavbarSlice(...a),
}));
