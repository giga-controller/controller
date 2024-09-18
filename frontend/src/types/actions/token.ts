import { z } from "zod";

export const tokenGetRequestSchema = z.object({
  api_key: z.string(),
  table_name: z.string(),
});

export type TokenGetRequest = z.infer<typeof tokenGetRequestSchema>;

export const tokenGetResponseSchema = z.object({
  is_authenticated: z.boolean(),
});

export type TokenGetResponse = z.infer<typeof tokenGetResponseSchema>;
