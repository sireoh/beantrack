import { ItemCardDataModel } from "@/components/app/item-card/item-card";
import { WatchlistItem } from "@/models";
import { StateCreator } from "zustand";

export interface deleteDataModel {
  type: string;
  item: WatchlistItem | ItemCardDataModel;
}

export interface DialogState {
  isToggled: boolean;
  deleteData?: deleteDataModel;
  toggleDialog: () => void;
  setDeleteData: (data: deleteDataModel | undefined) => void;
}

export const createDialogSlice: StateCreator<{
  dialog: DialogState;
}> = (set) => ({
  dialog: {
    isToggled: false,
    deleteData: undefined,
    toggleDialog: () =>
      set((state) => ({
        dialog: {
          ...state.dialog,
          isToggled: !state.dialog.isToggled,
        },
      })),
    setDeleteData: (data) =>
      set((state) => ({
        dialog: {
          ...state.dialog,
          deleteData: data,
        },
      })),
  },
});
