// hooks/useAuth.ts
"use client";
import { useStore } from "@/store";
import { useEffect } from "react";
import { getAuth } from "@/api/api";

export type User = {
  username: string;
  avatar?: string;
  admin: boolean;
};

export function useAuth() {
  const { user, loading, setUser, setLoading } = useStore(
    (state) => state.session
  );

  useEffect(() => {
    async function checkAuth() {
      try {
        const data = await getAuth();
        setUser(data);
      } catch {
        setUser(undefined);
      } finally {
        setLoading(false);
      }
    }

    checkAuth();
  }, []);

  return { user, loading };
}
