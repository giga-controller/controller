import { Button } from "@/components/ui/button";
import { Message } from "@/types/actions/query/base";

type ClearButtonProps = {
  updateChatHistory: (newChatHistory: Message[]) => void;
  updateInstance: (instance: string | null) => void;
};

export default function ClearButton({
  updateChatHistory,
  updateInstance,
}: ClearButtonProps) {
  return (
    <Button
      className="text-xs h-6 bg-opacity-20 backdrop-blur transition-none hover:bg-opacity-50 hover:opacity-100"
      onClick={() => {
        updateChatHistory([]);
        updateInstance(null);
      }}
    >
      CLEAR
    </Button>
  );
}
