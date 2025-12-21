// hooks/useAuth.ts
"use client";
import { useStore } from "@/store";
import { useEffect } from "react";

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
        const res = await fetch("/api/auth", {
          credentials: "include",
        });
        if (res.ok) {
          const data = await res.json();
          setUser(data);
        } else {
          setUser(undefined);
        }
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
