import { z } from "zod";

export const loginRequestSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string(),
});

export type LoginRequest = z.infer<typeof loginRequestSchema>;

export const loginResponseSchema = z.object({
  api_key: z.string(),
});

export type LoginResponse = z.infer<typeof loginResponseSchema>;
