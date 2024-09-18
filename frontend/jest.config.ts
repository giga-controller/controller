import nextJest from "next/jest.js";

import type { Config } from "jest";

const createJestConfig = nextJest({
  dir: "./",
});

const config: Config = {
  clearMocks: true,
  collectCoverage: true,
  coverageDirectory: "coverage",
  coverageProvider: "v8",
  verbose: true,
  preset: "ts-jest",
  testEnvironment: "jest-environment-jsdom",
  testPathIgnorePatterns: ["/node_modules/", "/e2e/"],
  setupFiles: ["<rootDir>/.jest/setEnvVars.ts"],
  setupFilesAfterEnv: ["<rootDir>/.jest/jest.setup.ts"],
};

export default createJestConfig(config);
