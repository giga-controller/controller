import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import FeedbackForm from "./form";
import { useState } from "react";
import { FeedbackRequest } from "@/types/actions/feedback/form";
import { submitFeedback } from "@/actions/feedback/submit";

export default function FeedbackButton() {
  const [open, setOpen] = useState<boolean>(false);

  const handleSubmitFeedback = async (values: FeedbackRequest) => {
    await submitFeedback(values);
    setOpen(false);
  };
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        className="ml-1 mr-1 p-1 rounded border border-input bg-background hover:bg-accent hover:text-accent-foreground shadow-sm"
        aria-label="Report an issue"
      >
        Feedback
      </DialogTrigger>
      <DialogContent>
        <DialogHeader className="flex flex-col items-center justify-center">
          <DialogTitle>Give us your feedback</DialogTitle>
        </DialogHeader>
        <FeedbackForm handleSubmitFeedback={handleSubmitFeedback} />
      </DialogContent>
    </Dialog>
  );
}
