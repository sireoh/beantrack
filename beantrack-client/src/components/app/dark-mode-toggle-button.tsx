"use client";

import React, { useState } from "react";
import { Button } from "../ui/button";
import { cn } from "@/lib/utils";
import { useTheme } from "next-themes";
import { DropdownMenuItem } from "../ui/dropdown-menu";
import { Moon } from "lucide-react";

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
    <DropdownMenuItem asChild onClick={toggleDarkMode}>
      <div className="flex justify-between items-center w-full text-info">
        <Moon />
        Dark Mode
        <Button className={cn(_darkModeMainClasses, getCurrentDynamicClass())}>
          {theme == "dark" ? "ON" : "OFF"}
        </Button>
      </div>
    </DropdownMenuItem>
  );
};

export default DarkModeToggleButton;
