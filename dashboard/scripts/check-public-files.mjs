// Build-time guard on public/data (the JavaScript twin of
// scripts/check_public_data.py). Fails the build if a public file carries
// record identifiers, weights or record counts, a withheld cell that still
// has a value, or area codes; or if results.json carries placeholder
// measures without its placeholder flag and notice.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const FORBIDDEN = /(^|_)(household_id|person_id|benunit_id|weight|weights|record_id|sernum|records|n_records|sample_size)$/;
const AREA_CODE = /\b[ENSWK]\d{8}\b/;
const dir = new URL("../public/data/", import.meta.url).pathname;
const problems = [];

function walk(obj, where) {
  if (Array.isArray(obj)) return obj.forEach((v, i) => walk(v, `${where}[${i}]`));
  if (obj && typeof obj === "object") {
    for (const [k, v] of Object.entries(obj)) {
      if (FORBIDDEN.test(k)) problems.push(`${where}.${k}: identifier, weight or count`);
      walk(v, `${where}.${k}`);
    }
    if (obj.withheld === true && Object.entries(obj).some(([k, v]) => k !== "withheld" && typeof v === "number")) {
      problems.push(`${where}: withheld cell carries a value`);
    }
  }
}

function files(root) {
  return readdirSync(root).flatMap((name) => {
    const p = join(root, name);
    return statSync(p).isDirectory() ? files(p) : [p];
  });
}

for (const file of files(dir)) {
  const text = readFileSync(file, "utf8");
  if (AREA_CODE.test(text)) problems.push(`${file}: area codes present`);
  if (file.endsWith(".json")) {
    const data = JSON.parse(text);
    walk(data, file);
    if (file.endsWith("results.json")) {
      const anyPlaceholder = (data.measures ?? []).some((m) => m.status !== "announced");
      if (anyPlaceholder && !(data.meta?.placeholder === true && /placeholder/i.test(data.meta?.notice ?? ""))) {
        problems.push(`${file}: placeholder measures without the placeholder flag and notice`);
      }
    }
  } else if (!file.endsWith(".csv") && !file.endsWith(".gitkeep")) {
    problems.push(`${file}: only .json and .csv are allowed`);
  }
}

for (const p of problems) console.error(p);
console.log(`${problems.length} problem(s) in public/data`);
process.exit(problems.length ? 1 : 0);
