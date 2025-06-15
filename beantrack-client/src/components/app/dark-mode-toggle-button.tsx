"use client";

import React, { useState } from "react";
import { Button } from "../ui/button";
import { cn } from "@/lib/utils";
import { useTheme } from "next-themes";

const DarkModeToggleButton = () => {
  const { setTheme, theme } = useTheme();
  const _darkModeMainClasses = "ml-auto p-2 font-bold text-white";
  enum _dynamicClasses {
    DARK = "bg-green-500 hover:bg-green-600",
    LIGHT = "bg-red-500 hover:bg-red-600",
  }

  function toggleDarkMode() {
    if (theme == "dark") {
      setTheme("light");
    } else {
      setTheme("dark");
    }
  }

  function getCurrentDynamicClass() {
    if (theme == "dark") {
      return cn(_darkModeMainClasses, _dynamicClasses.DARK);
    } else {
      return cn(_darkModeMainClasses, _dynamicClasses.LIGHT);
    }
  }

  return (
    <Button
      className={cn(_darkModeMainClasses, getCurrentDynamicClass())}
      onClick={toggleDarkMode}>
      {theme == "dark" ? "ON" : "OFF"}
    </Button>
  );
};

export default DarkModeToggleButton;
