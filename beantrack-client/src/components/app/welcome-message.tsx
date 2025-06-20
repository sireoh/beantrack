"use client";
import { useAuth } from "@/hooks/use-auth";

const WelcomeMessage = () => {
  const { user, loading } = useAuth();
  return (
    <div className="flex items-center h-full mt-1 mx-2">
      <span className="text-white">
        Hello&nbsp;
        <span className="text-red-500 font-bold">
          {loading ? "..." : user?.username || "Guest"}
        </span>
        !
      </span>
    </div>
  );
};

export default WelcomeMessage;
