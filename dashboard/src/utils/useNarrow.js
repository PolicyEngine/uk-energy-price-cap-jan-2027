"use client";

import { useEffect, useState } from "react";

export const NARROW_QUERY = "(max-width: 639px)";

/** True below 640 px (phones). False on the server and before mounting. */
export default function useNarrow() {
  const [narrow, setNarrow] = useState(false);
  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return undefined;
    const query = window.matchMedia(NARROW_QUERY);
    const update = () => setNarrow(query.matches);
    update();
    query.addEventListener?.("change", update);
    return () => query.removeEventListener?.("change", update);
  }, []);
  return narrow;
}
