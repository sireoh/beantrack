import { User } from "@/hooks/use-auth";
import { StateCreator } from "zustand";

export interface SessionState {
  user: User | undefined;
  loading: boolean;
  setUser: (new_user: User | undefined) => void;
  setLoading: (new_loading: boolean) => void;
}

export const createSessionSlice: StateCreator<{
  session: SessionState;
}> = (set) => ({
  session: {
    user: undefined,
    loading: true,

    setUser: (new_user: User | undefined) => {
      set((state) => ({
        session: {
          ...state.session,
          user: new_user,
        },
      }));
    },

    setLoading: (new_loading: boolean) => {
      set((state) => ({
        session: {
          ...state.session,
          loading: new_loading,
        },
      }));
    },
  },
});
