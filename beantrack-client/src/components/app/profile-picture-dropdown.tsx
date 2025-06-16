import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ChevronDown, Clapperboard, LogOut, Settings, Tv } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import Link from "next/link";
import DarkModeToggleButton from "./dark-mode-toggle-button";

const ProfilePictureDropdown = () => {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <div className="flex items-center cursor-pointer space-x-2">
          <Avatar className="w-8 h-8">
            <AvatarImage
              src={
                process.env.NEXT_PUBLIC_USER_AVATAR_URL || "/default-avatar.png"
              }
              alt="User avatar"
            />
            <AvatarFallback>U</AvatarFallback>
          </Avatar>
          <ChevronDown className="w-4 h-4 text-white" />
        </div>
      </DropdownMenuTrigger>

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
