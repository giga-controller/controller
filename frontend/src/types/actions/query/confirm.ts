import { z } from "zod";
import { integrationEnum } from "@/types/integration";
import { messageSchema } from "@/types/actions/query/base";

export const confirmRequestSchema = z.object({
  chat_history: z.array(messageSchema),
  api_key: z.string(),
  enable_verification: z.boolean(),
  integrations: z.array(integrationEnum),
  function_to_verify: z.string(),
  instance: z.string().nullable(),
});

export type ConfirmRequest = z.infer<typeof confirmRequestSchema>;

export const userVerificationSchema = z.enum(["YES", "NO"]);
