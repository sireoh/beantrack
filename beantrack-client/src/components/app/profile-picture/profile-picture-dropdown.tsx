"use client";

import { Clapperboard, Settings, Tv } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import Link from "next/link";
import DarkModeToggleButton from "./dark-mode-toggle-button";
import ProfilePicture from "./profile-picture";
import LogoutButton from "./logout-button";
import { useStore } from "@/store";

const ProfilePictureDropdown = () => {
  const { user, loading } = useStore((state) => state.session);

  return (
    <DropdownMenu>
      <ProfilePicture />

      <DropdownMenuContent className="w-48">
        {!loading && user?.username && (
          <>
            <DropdownMenuItem asChild>
              <Link href={`/tvlist/${user.username}`}>
                <Tv />
                TV List
              </Link>
            </DropdownMenuItem>

            <DropdownMenuItem asChild>
              <Link href={`/movielist/${user.username}`}>
                <Clapperboard />
                Movie List
              </Link>
            </DropdownMenuItem>
          </>
        )}

        <DropdownMenuItem asChild>
          <Link href="/settings">
            <Settings />
            Settings
          </Link>
        </DropdownMenuItem>

        <DarkModeToggleButton />

        <DropdownMenuSeparator />

        <LogoutButton />
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default ProfilePictureDropdown;
