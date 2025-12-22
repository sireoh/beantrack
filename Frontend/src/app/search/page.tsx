"use client";

import { Suspense } from "react";
import { SearchPageContent } from "./SearchPageContent";

export default function Home() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <SearchPageContent />
    </Suspense>
  );
}
