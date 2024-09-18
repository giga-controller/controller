import { z } from "zod";

export const tokenPostRequestSchema = z.object({
  api_key: z.string(),
  access_token: z.string(),
  refresh_token: z.string().nullable(),
  client_id: z.string(),
  client_secret: z.string(),
  table_name: z.string(),
});

export type TokenPostRequest = z.infer<typeof tokenPostRequestSchema>;

export const requestTypeSchema = z.enum(["GET", "POST"]);

export type RequestType = z.infer<typeof requestTypeSchema>;
