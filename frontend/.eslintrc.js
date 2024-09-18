module.exports = {
  root: true,
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "next/core-web-vitals",
    "prettier",
  ],
  ignorePatterns: [
    "node_modules/",
    "dist/",
    "src/components/ui/*.tsx",
    "src/components/ui/*.ts",
  ],
  rules: {
    curly: "error",
    "no-shadow": "error",
    "no-nested-ternary": "error",
    "@typescript-eslint/no-unused-vars": "warn",
    "no-restricted-exports": [
      "error",
      {
        restrictDefaultExports: {
          direct: false,
          named: true,
          defaultFrom: true,
          namedFrom: true,
          namespaceFrom: true,
        },
      },
    ],
    "react/jsx-sort-props": [
      "error",
      {
        noSortAlphabetically: true,
        shorthandLast: true,
        callbacksLast: true,
      },
    ],
    "react/no-array-index-key": "warn",
    "react/no-danger": "warn",
    "react/self-closing-comp": "error",
    "react/function-component-definition": [
      "warn",
      {
        namedComponents: "function-declaration",
        unnamedComponents: "arrow-function",
      },
    ],
    "jsx-a11y/alt-text": "error",
    "import/no-extraneous-dependencies": [
      "error",
      {
        packageDir: __dirname,
      },
    ],
  },
};
