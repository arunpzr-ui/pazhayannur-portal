/**
 * Processes the annual development plan (plan.xlsx) into src/data/focus.json.
 *
 * Usage:
 *   npm install -D xlsx
 *   node scripts/process-plan.js path/to/plan.xlsx
 *
 * The "Sector" column in the source file uses ~27 raw Kerala LSGD scheme
 * categories, not our old 13-slug list. SECTOR_MAP below consolidates them
 * into 14 sectors by real budget share (verified to reconcile exactly to
 * the source total, with no project dropped or double-counted). Re-check
 * that reconciliation (the script prints it) if next year's plan
 * introduces a sector name not listed here.
 */
import XLSX from "xlsx";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const inputPath = process.argv[2];

if (!inputPath) {
  console.error("Usage: node scripts/process-plan.js path/to/plan.xlsx");
  process.exit(1);
}

const OUTPUT_PATH = path.resolve(__dirname, "../src/data/focus.json");
const PLAN_YEAR = "2026-27";
const MEGA_PROJECT_COUNT = 5;
const TOP_PROJECTS_PER_SECTOR = 5;

// Raw "Sector" values (Malayalam, as written in the source file) grouped
// into consolidated sectors. Order here doesn't matter — sectors are
// re-sorted by total budget when the output is built.
const SECTOR_MAP = {
  "housing-electrification": {
    title: "Housing & Electrification",
    ml: "പാർപ്പിടവും വൈദ്യുതീകരണവും",
    raw: ["പാര്‍പ്പിടം,വീട് വൈദ്യുതീകരണം, ചേരിവികസനം"],
  },
  transportation: {
    title: "Transportation & Roads",
    ml: "ഗതാഗതം",
    raw: ["ഗതാഗതം"],
  },
  agriculture: {
    title: "Agriculture",
    ml: "കൃഷി",
    raw: ["കൃഷി"],
  },
  "drinking-water": {
    title: "Drinking water",
    ml: "കുടിവെള്ളം",
    raw: ["കുടിവെള്ളം"],
  },
  "public-works": {
    title: "Public Works & Buildings",
    ml: "പൊതുമരാമത്ത്",
    raw: [
      "ഉല്പാദനസേവന മേഖലകളില്‍ ഉള്‍പ്പെടാത്ത പൊതുകെട്ടിടങ്ങള്‍",
      "മറ്റ് നിര്‍മ്മാണ പ്രവൃത്തികള്‍",
    ],
  },
  "education-art-culture": {
    title: "Education, Arts & Culture",
    ml: "വിദ്യാഭ്യാസം, കല, സംസ്കാരം",
    raw: [
      "വിദ്യാഭ്യാസം",
      "വായനശാലകള്, ലൈബ്രറികള്, ഗ്രാമസഭാ/വാര്ഡ്സഭാ കേന്ദ്രങ്ങള്",
      "കലാസാംസ്കാരികകായിക വികസനം, യുവജനക്ഷേമം",
    ],
  },
  "animal-husbandry": {
    title: "Animal Husbandry, Dairy & Fisheries",
    ml: "മൃഗസംരക്ഷണവും ക്ഷീരവികസനവും",
    raw: ["മൃഗസംരക്ഷണം", "ക്ഷീരവികസനം", "മത്സ്യബന്ധനം"],
  },
  "social-welfare": {
    title: "Social Welfare & Security",
    ml: "സാമൂഹ്യക്ഷേമം, സാമൂഹ്യസുരക്ഷിതത്വം",
    raw: ["സാമൂഹ്യക്ഷേമം, സാമൂഹ്യസുരക്ഷിതത്വം"],
  },
  energy: {
    title: "Energy & Electrification",
    ml: "ഊർജ്ജവും വൈദ്യുതീകരണവും",
    raw: ["തെരുവ് വിളക്ക്, ഓഫീസ് വൈദ്യുതീകരണം", "ഊര്‍ജ്ജസംരക്ഷണം"],
  },
  health: {
    title: "Health",
    ml: "ആരോഗ്യം",
    raw: ["ആരോഗ്യം"],
  },
  "local-economic-development": {
    title: "Local Economic Development",
    ml: "തദ്ദേശീയ സാമ്പത്തിക വികസനം",
    raw: [
      "ചെറുകിട വ്യവസായം",
      "വ്യവസായം, സ്വയം തൊഴില്‍ സംരംഭങ്ങള്‍, വിപണന പ്രോത്സാഹനം",
      "തൊഴില്‍ വൈദഗ്ദ്ധ്യപോഷണം",
    ],
  },
  "sanitation-waste": {
    title: "Sanitation & Waste Management",
    ml: "ശുചിത്വവും മാലിന്യ സംസ്കരണവും",
    raw: ["ഖരമാലിന്യ പരിപാലനം", "ദ്രവമാലിന്യ പരിപാലനം", "പൊതു ശുചിത്വം"],
  },
  "women-child-development": {
    title: "Women & Child Development",
    ml: "വനിതാ — ശിശു വികസനം",
    raw: ["അംഗന്‍വാടികള്‍", "പോഷകാഹാരം"],
  },
  "good-governance": {
    title: "Good Governance",
    ml: "സദ്ഭരണം",
    raw: [
      "കമ്പ്യൂട്ടര്‍വത്കരണവും സേവനം മെച്ചപ്പെടുത്തലും",
      "പദ്ധതി രൂപീകരണം, നിര്‍വ്വഹണം, മോണിറ്ററിംഗ്",
      "സര്‍ക്കാര്‍ ഉത്തരവ് / മറ്റ് ഉത്തരവ് പ്രകാരമുള്ള പ്രോജക്ടുകള്‍",
    ],
  },
};

// Reverse lookup: raw sector string -> consolidated slug.
const RAW_TO_SLUG = new Map();
for (const [slug, def] of Object.entries(SECTOR_MAP)) {
  for (const raw of def.raw) RAW_TO_SLUG.set(raw, slug);
}

/** "Fund X - 4000000 , Fund Y - 250002" -> [{ source, amount }] */
function parseFundBreakdown(desc) {
  return desc.split(",").map((part) => {
    const match = part.trim().match(/^(.+?)\s*-\s*(\d+)$/);
    if (!match) {
      throw new Error(`Could not parse fund description segment: "${part}"`);
    }
    return { source: match[1].trim(), amount: Number(match[2]) };
  });
}

function toProject(row) {
  return {
    nameEn: row["Project Name Eng"],
    nameMl: row["Project Name Mal"],
    sector: row["Sector"],
    fundTotal: Number(row["FundTotal"]),
    fundBreakdown: parseFundBreakdown(String(row["Fund Description"])),
  };
}

const workbook = XLSX.readFile(inputPath);
const sheet = workbook.Sheets[workbook.SheetNames[0]];
const rows = XLSX.utils.sheet_to_json(sheet);

if (rows.length === 0) {
  console.error("No rows found in the first sheet of", inputPath);
  process.exit(1);
}

const projects = rows.map(toProject);

// Fail loudly on any sector the map doesn't know about, rather than
// silently dropping projects from the published total.
const unmapped = new Set(
  projects.map((p) => p.sector).filter((s) => !RAW_TO_SLUG.has(s)),
);
if (unmapped.size > 0) {
  console.error("Unmapped sector(s) found in source file — add them to SECTOR_MAP:");
  for (const s of unmapped) console.error(" -", s);
  process.exit(1);
}

const totalBudget = projects.reduce((sum, p) => sum + p.fundTotal, 0);

const megaProjects = [...projects]
  .sort((a, b) => b.fundTotal - a.fundTotal)
  .slice(0, MEGA_PROJECT_COUNT)
  .map(({ nameEn, nameMl, sector, fundTotal, fundBreakdown }) => ({
    nameEn,
    nameMl,
    sector: SECTOR_MAP[RAW_TO_SLUG.get(sector)].title,
    fundTotal,
    fundBreakdown,
  }));

const bySlug = new Map(Object.keys(SECTOR_MAP).map((slug) => [slug, []]));
for (const p of projects) bySlug.get(RAW_TO_SLUG.get(p.sector)).push(p);

const sectors = Object.entries(SECTOR_MAP)
  .map(([slug, def]) => {
    const sectorProjects = bySlug.get(slug);
    const sectorTotal = sectorProjects.reduce((sum, p) => sum + p.fundTotal, 0);
    const topProjects = [...sectorProjects]
      .sort((a, b) => b.fundTotal - a.fundTotal)
      .slice(0, TOP_PROJECTS_PER_SECTOR)
      .map(({ nameEn, nameMl, fundTotal, fundBreakdown }) => ({
        nameEn,
        nameMl,
        fundTotal,
        fundBreakdown,
      }));
    return {
      slug,
      title: def.title,
      ml: def.ml,
      projectCount: sectorProjects.length,
      totalBudget: sectorTotal,
      topProjects,
    };
  })
  .sort((a, b) => b.totalBudget - a.totalBudget)
  .map((sector, i) => ({
    code: `F / ${String(i + 1).padStart(2, "0")}`,
    ...sector,
  }));

// Reconciliation check: every rupee must land in exactly one sector.
const sectorSum = sectors.reduce((sum, s) => sum + s.totalBudget, 0);
if (sectorSum !== totalBudget) {
  console.error(
    `Reconciliation failed: sectors sum to ${sectorSum}, but total is ${totalBudget}.`,
  );
  process.exit(1);
}

const output = {
  year: PLAN_YEAR,
  totalBudget,
  totalProjects: projects.length,
  megaProjects,
  sectors,
};

fs.writeFileSync(OUTPUT_PATH, JSON.stringify(output, null, 2) + "\n", "utf8");

console.log(`Wrote ${OUTPUT_PATH}`);
console.log(`Projects: ${projects.length}`);
console.log(`Total budget: ${totalBudget.toLocaleString("en-IN")}`);
console.log(`Sectors: ${sectors.length} (reconciled: ${sectorSum === totalBudget})`);
console.table(
  sectors.map((s) => ({
    code: s.code,
    title: s.title,
    projects: s.projectCount,
    budget: s.totalBudget.toLocaleString("en-IN"),
  })),
);
