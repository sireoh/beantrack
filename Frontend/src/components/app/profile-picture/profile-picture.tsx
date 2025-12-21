"use client";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ChevronDown, User } from "lucide-react";
import { DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { useStore } from "@/store";

const ProfilePicture = () => {
  const { user, loading } = useStore((state) => state.session);
  const url = `https://res.cloudinary.com/beantrack/image/upload/${user?.avatar}.gif`;

  return (
    <DropdownMenuTrigger asChild>
      <div className="flex items-center cursor-pointer space-x-2">
        <Avatar className="w-8 h-8">
          <AvatarImage
            src={loading ? "..." : url || "Guest"}
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
