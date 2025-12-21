import { StateCreator } from "zustand";

export interface NavbarState {
  isExpanded: boolean;
  toggleExpand: () => void;
}

export const createNavbarSlice: StateCreator<{
  navbar: NavbarState;
}> = (set) => ({
  navbar: {
    isExpanded: false,

    toggleExpand: () => {
      set((state) => ({
        navbar: {
          ...state.navbar,
          isExpanded: !state.navbar.isExpanded,
        },
      }));
    },
  },
});
