import { z } from "zod";
import { integrationEnum } from "@/types/integration";

export const roleSchema = z.enum(["user", "assistant"]);

export type Role = z.infer<typeof roleSchema>;

export const messageSchema = z.object({
  role: roleSchema,
  content: z.string().min(1),
  data: z.array(z.record(z.any())).nullable(),
});

export type Message = z.infer<typeof messageSchema>;

export const queryRequestSchema = z.object({
  message: messageSchema,
  chat_history: z.array(messageSchema),
  api_key: z.string(),
  enable_verification: z.boolean(),
  integrations: z.array(integrationEnum),
  instance: z.string().nullable(),
});

export type QueryRequest = z.infer<typeof queryRequestSchema>;

export const queryResponseSchema = z.object({
  chat_history: z.array(messageSchema),
  instance: z.string().nullable(),
  function_to_verify: z.string().nullable(),
});

export type QueryResponse = z.infer<typeof queryResponseSchema>;
