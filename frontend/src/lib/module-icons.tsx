import {
  BarChart3,
  Brain,
  Database,
  FileText,
  FlaskConical,
  GraduationCap,
  Layers,
  LineChart,
  Search,
  Shield,
  SlidersHorizontal,
  Sparkles,
  type LucideIcon,
} from "lucide-react";
import type { ModuleGroup } from "@/lib/modules";

export const MODULE_ICONS: Record<ModuleGroup["icon"], LucideIcon> = {
  database: Database,
  chart: BarChart3,
  sliders: SlidersHorizontal,
  brain: Brain,
  layers: Layers,
  lineChart: LineChart,
  search: Search,
  sparkles: Sparkles,
  flask: FlaskConical,
  fileText: FileText,
  graduation: GraduationCap,
  shield: Shield,
};

const FAMILY_LABEL: Record<string, string> = {
  supervised: "Supervised",
  unsupervised: "Unsupervised",
  timeseries: "Time series",
  any: "All families",
};

export function familyBadge(requires: ModuleGroup["requires"]): string {
  if (requires.includes("any")) return FAMILY_LABEL.any;
  return requires.map((r) => FAMILY_LABEL[r] ?? r).join(" · ");
}
