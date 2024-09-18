import { z } from "zod";

export const feedbackRequestSchema = z.object({
  id: z.string().nullable(),
  feedback: z.string().min(1, "Feedback is required"),
});

export type FeedbackRequest = z.infer<typeof feedbackRequestSchema>;
