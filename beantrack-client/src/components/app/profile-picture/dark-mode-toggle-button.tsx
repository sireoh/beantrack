"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { Moon, Power, PowerOff } from "lucide-react";
import { DropdownMenuItem } from "../../ui/dropdown-menu";
import { Button } from "../../ui/button";
import { cn } from "@/lib/utils";

const DarkModeToggleButton = () => {
  const { setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Required to prevent hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  const isDark = resolvedTheme === "dark";
  const iconColor = "text-white";
  const iconStrokeWidth = 4;

  const toggleDarkMode = () => {
    setTheme(isDark ? "light" : "dark");
  };

  return (
    <DropdownMenuItem asChild>
      <div
        className="flex justify-between items-center w-full text-info cursor-pointer"
        onClick={toggleDarkMode}>
        <Moon />
        Dark Mode
        <Button
          className={cn(
            "ml-auto size-6 rounded-full",
            isDark
              ? "bg-green-500 hover:bg-green-600"
              : "bg-red-500 hover:bg-red-600"
          )}>
          {isDark ? (
            <Power className={iconColor} strokeWidth={iconStrokeWidth} />
          ) : (
            <PowerOff className={iconColor} strokeWidth={iconStrokeWidth} />
          )}
        </Button>
      </div>
    </DropdownMenuItem>
  );
};

export default DarkModeToggleButton;
