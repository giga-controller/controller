"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useUser } from "@clerk/nextjs";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { DialogClose, DialogFooter } from "@/components/ui/dialog";
import {
  FeedbackRequest,
  feedbackRequestSchema,
} from "@/types/actions/feedback/form";

interface ReportFormProps {
  handleSubmitFeedback: (values: FeedbackRequest) => void;
}

export default function FeedbackForm({
  handleSubmitFeedback,
}: ReportFormProps) {
  const { user } = useUser();

  const form = useForm<FeedbackRequest>({
    resolver: zodResolver(feedbackRequestSchema),
    defaultValues: {
      id: user?.id || null,
      feedback: "",
    },
  });

  function onSubmit(values: FeedbackRequest) {
    handleSubmitFeedback(values);
  }

  return (
    <Form {...form}>
      <form
        className="space-y-4 max-h-96"
        onSubmit={form.handleSubmit(onSubmit)}
      >
        <FormField
          control={form.control}
          name="feedback"
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <Textarea className="max-h-80" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <DialogFooter className="sm:justify-end">
          <Button type="submit">Submit</Button>
          <DialogClose asChild>
            <Button type="button" variant="secondary">
              Close
            </Button>
          </DialogClose>
        </DialogFooter>
      </form>
    </Form>
  );
}
