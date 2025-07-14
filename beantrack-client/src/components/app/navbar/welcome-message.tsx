"use client";

import { useStore } from "@/store";

const WelcomeMessage = () => {
  const { user, loading } = useStore((state) => state.session);
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
