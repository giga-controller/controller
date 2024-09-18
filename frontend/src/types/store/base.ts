import { z } from "zod";
import { create } from "zustand";
import { persist } from "zustand/middleware";

export const createPersistedStore = <T, K extends string, S extends string>(
  storeName: string,
  defaultState: T,
  stateSchema: z.ZodSchema<T>,
  stateKey: K,
  setStateKey: S,
) => {
  type StoreType = {
    [key in K]: T;
  } & {
    [key in S]: (newState: Partial<T>) => void;
  };

  return create<StoreType>()(
    persist(
      (set) =>
        ({
          [stateKey]: defaultState,
          [setStateKey]: (newState: Partial<T>) =>
            set((store) => {
              const updatedState = { ...store[stateKey], ...newState };
              const result = stateSchema.safeParse(updatedState);
              if (!result.success) {
                return store; // Return the original store if validation fails
              }

              return { ...store, [stateKey]: updatedState };
            }),
        }) as StoreType,
      {
        name: storeName,
        getStorage: () => localStorage,
        onRehydrateStorage: () => (state) => {
          if (state && stateKey in state) {
            const result = stateSchema.safeParse(state[stateKey]);
            if (!result.success) {
              return { [stateKey]: defaultState };
            }
          }
        },
      },
    ),
  );
};
