import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
  {
    rules: {
      // Data-load / URL-sync effects set state after fetch; the new React Compiler
      // rule is too strict for our intake + shell patterns (ADR-0011 CI hygiene).
      "react-hooks/set-state-in-effect": "off",
    },
  },
]);

export default eslintConfig;
