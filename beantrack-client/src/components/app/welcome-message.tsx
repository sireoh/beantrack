import React from "react";

const WelcomeMessage = () => {
  return (
    <div className="flex items-center h-full mt-1 mx-2">
      <span className="text-white">
        Hello&nbsp;
        <span className="text-red-500 font-bold">
          {process.env.NEXT_PUBLIC_USERNAME}
        </span>
        !
      </span>
    </div>
  );
};

export default WelcomeMessage;
