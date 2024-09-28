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
        className="mx-1 px-4 py-1.5 rounded border border-input bg-green-500 hover:bg-green-700 hover:text-white shadow-sm"
        aria-label="Feedback"
      >
        Feedback
      </DialogTrigger>
      <DialogContent>
        <DialogHeader className="flex flex-col items-center justify-center">
          <DialogTitle>How can we improve your experience?</DialogTitle>
        </DialogHeader>
        <FeedbackForm handleSubmitFeedback={handleSubmitFeedback} />
      </DialogContent>
    </Dialog>
  );
}
