"use client";

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AppRouterInstance } from "next/dist/shared/lib/app-router-context.shared-runtime";
import { usePathname, useRouter } from "next/navigation";
import React from "react";

type TabArrayType = { label: string; href: string }[];

interface WatchlistStatusTabsScreenProps {
  activeTab: string;
  tabs: TabArrayType;
  _hrefBase: string;
  router: AppRouterInstance;
}

function createTabArray(type: string): TabArrayType {
  var _allTabTitle = "";

  if (type == "tv") {
    _allTabTitle = "All TV Shows";
  } else if (type == "movie") {
    _allTabTitle = "All Movies";
  } else {
    _allTabTitle = "All";
  }

  return [
    { label: _allTabTitle, href: "" },
    { label: "Currently Watching", href: "watching" },
    { label: "Completed", href: "completed" },
    { label: "On Hold", href: "on_hold" },
    { label: "Dropped", href: "dropped" },
    { label: "Plan to Watch", href: "plan_to_watch" },
  ];
}

export const WatchlistStatusTabs = ({
  type,
  screenSize,
}: {
  type: string;
  screenSize?: string;
}) => {
  const router = useRouter();
  const pathname = usePathname();

  const tabs = createTabArray(type);
  const _hrefBase = `/${type}list/${process.env.NEXT_PUBLIC_USERNAME}/`;

  // Determine active tab by current URL
  const activeTab =
    tabs
      .slice() // create a copy
      .reverse() // check more specific routes first
      .find((tab) => pathname.endsWith("/" + tab.href))?.href || "";

  if (screenSize === "mobile") {
    return <WatchlistStatusTabsMobile />;
  } else {
    return (
      <WatchlistStatusTabsDesktop
        activeTab={activeTab}
        tabs={tabs}
        _hrefBase={_hrefBase}
        router={router}
      />
    );
  }
};

const WatchlistStatusTabsDesktop = ({
  activeTab,
  tabs,
  _hrefBase = "",
  router,
}: WatchlistStatusTabsScreenProps) => {
  return (
    <Tabs value={activeTab}>
      <TabsList className="p-0">
        {tabs.map((tab) => (
          <TabsTrigger
            key={tab.href}
            value={tab.href}
            onClick={() => router.push(_hrefBase + tab.href)}
            className={
              activeTab === tab.href
                ? "rounded-none"
                : "text-white rounded-none dark:text-white bg-sky-500"
            }>
            {tab.label}
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  );
};

const WatchlistStatusTabsMobile = () => {
  return "";
};
