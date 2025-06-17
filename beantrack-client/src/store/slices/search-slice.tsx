import { StateCreator } from "zustand";

export interface SearchState {
  currentType: string;
  updateCurrentType: (new_type: string) => void;
}

export const createSearchSlice: StateCreator<{
  search: SearchState;
}> = (set) => ({
  search: {
    currentType: "tv",

    updateCurrentType: (new_type: string) => {
      set((state) => ({
        search: {
          ...state.search,
          currentType: new_type,
        },
      }));
    },
  },
});
