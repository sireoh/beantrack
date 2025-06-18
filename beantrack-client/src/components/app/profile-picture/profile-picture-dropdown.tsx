import { Clapperboard, LogOut, Settings, Tv } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import Link from "next/link";
import DarkModeToggleButton from "../dark-mode-toggle-button";
import ProfilePicture from "./profile-picture";

const ProfilePictureDropdown = () => {
  return (
    <DropdownMenu>
      <ProfilePicture />

      <DropdownMenuContent className="w-48">
        <DropdownMenuItem asChild>
          <Link href={`/tvlist/${process.env.NEXT_PUBLIC_USERNAME}`}>
            <Tv />
            TV List
          </Link>
        </DropdownMenuItem>

        <DropdownMenuItem asChild>
          <Link href={`/movielist/${process.env.NEXT_PUBLIC_USERNAME}`}>
            <Clapperboard />
            Movie List
          </Link>
        </DropdownMenuItem>

        <DropdownMenuItem asChild>
          <Link href="/settings">
            <Settings />
            Settings
          </Link>
        </DropdownMenuItem>

        <DarkModeToggleButton />

        <DropdownMenuSeparator />

        <DropdownMenuItem asChild>
          <Link href="/logout">
            <LogOut />
            Logout
          </Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default ProfilePictureDropdown;
