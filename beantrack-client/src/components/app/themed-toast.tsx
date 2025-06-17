"use client";

import { useTheme } from "next-themes";
import React from "react";
import { Toaster } from "sonner";

const ThemedToast = () => {
  const { theme } = useTheme();

  return (
    <Toaster
      toastOptions={{
        style: {
          background:
            theme === "dark"
              ? "oklch(27.8% 0.033 256.848)"
              : "oklch(98.5% 0.002 247.839)",
          color:
            theme === "dark"
              ? "oklch(98.5% 0.002 247.839)"
              : "oklch(27.8% 0.033 256.848)",
          border:
            theme === "dark"
              ? "oklch(98.5% 0.002 247.839)"
              : "oklch(27.8% 0.033 256.848)",
        },
      }}
    />
  );
};

export default ThemedToast;
