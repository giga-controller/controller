import {
  defaultIntegrationsState,
  integrationsStateSchema,
} from "@/types/integration";
import { createPersistedStore } from "@/types/store/base";

export const useIntegrationsStore = createPersistedStore(
  "integrations",
  defaultIntegrationsState,
  integrationsStateSchema,
  "integrationsState",
  "setIntegrationsState",
);
