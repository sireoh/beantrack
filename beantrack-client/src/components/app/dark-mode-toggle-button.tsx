"use client";

import React, { useState } from "react";
import { Button } from "../ui/button";
import { cn } from "@/lib/utils";
import { useTheme } from "next-themes";
import { DropdownMenuItem } from "../ui/dropdown-menu";
import { Moon, Power, PowerOff } from "lucide-react";

const DarkModeToggleButton = () => {
  const { setTheme, theme } = useTheme();
  const _iconColor = "text-white";
  const _iconStrokeWidth = 4;

  function toggleDarkMode() {
    if (theme == "dark") {
      setTheme("light");
    } else {
      setTheme("dark");
    }
  }

  return (
    <DropdownMenuItem asChild onClick={toggleDarkMode}>
      <div className="flex justify-between items-center w-full text-info">
        <Moon />
        Dark Mode
        <Button
          className={cn(
            "ml-auto size-6 rounded-full",
            theme == "dark"
              ? "bg-green-500 hover:bg-green-600"
              : "bg-red-500 hover:bg-red-600"
          )}>
          {theme == "dark" ? (
            <Power className={_iconColor} strokeWidth={_iconStrokeWidth} />
          ) : (
            <PowerOff className={_iconColor} strokeWidth={_iconStrokeWidth} />
          )}
        </Button>
      </div>
    </DropdownMenuItem>
  );
};

export default DarkModeToggleButton;
