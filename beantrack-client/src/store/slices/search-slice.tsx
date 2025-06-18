import { StateCreator } from "zustand";

export interface SearchState {
  value: string;
  currentType: string;
  setValue: (new_value: string) => void;
  updateCurrentType: (new_type: string) => void;
}

export const createSearchSlice: StateCreator<{
  search: SearchState;
}> = (set) => ({
  search: {
    value: "",
    currentType: process.env.SEARCH_TYPE_BUTTON_DEFAULT_VALUE || "tv",

    setValue: (new_value: string) => {
      set((state) => ({
        search: {
          ...state.search,
          value: new_value,
        },
      }));
    },

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
