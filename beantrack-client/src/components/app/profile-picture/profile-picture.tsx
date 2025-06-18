import React from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ChevronDown, User } from "lucide-react";
import { DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

const ProfilePicture = () => {
  return (
    <DropdownMenuTrigger asChild>
      <div className="flex items-center cursor-pointer space-x-2">
        <Avatar className="w-8 h-8">
          <AvatarImage
            src={process.env.NEXT_PUBLIC_USER_AVATAR_URL}
            alt="User avatar"
          />
          <AvatarFallback className="text-gray-300 bg-gray-700 dark:text-gray-700 dark:bg-gray-300">
            <User />
          </AvatarFallback>
        </Avatar>
        <ChevronDown className="w-4 h-4 text-white" />
      </div>
    </DropdownMenuTrigger>
  );
};

export default ProfilePicture;
