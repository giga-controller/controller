import { Button } from "@/components/ui/button";
import { userVerificationSchema } from "@/types/actions/query/confirm";
import { useEffect } from "react";

type VerificationOptionProps = {
  isEnabled: boolean;
  sendMessage: (input: string) => void;
};

export default function VerificationOption({
  isEnabled,
  sendMessage,
}: VerificationOptionProps) {
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (!isEnabled) return;
      
      if (event.key === "Enter") {
        sendMessage(userVerificationSchema.Values.YES);
      } else if (event.key === "Backspace") {
        sendMessage(userVerificationSchema.Values.NO);
      }
    };

    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
  }, [isEnabled, sendMessage]);

  if (!isEnabled) {
    return null;
  }

  return (
    <div className="absolute inset-0 flex items-center justify-center space-x-4">
      <Button onClick={() => sendMessage(userVerificationSchema.Values.YES)}>
        YES (Enter)
      </Button>
      <Button onClick={() => sendMessage(userVerificationSchema.Values.NO)}>
        NO (Backspace)
      </Button>
    </div>
  );
}
