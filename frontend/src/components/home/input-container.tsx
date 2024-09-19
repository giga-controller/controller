import Loader from "@/components/accessory/loader";
import VerificationOption from "@/components/home/input/verification-option";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { userVerificationSchema } from "@/types/actions/query/confirm";
import { useEffect, useRef, useState } from "react";

type InputContainerProps = {
  isApiKeyLoading: boolean;
  isResponseFetching: boolean;
  functionToVerify: string | null;
  sendMessage: (inputText: string) => void;
};

export default function InputContainer({
  isApiKeyLoading,
  isResponseFetching,
  functionToVerify,
  sendMessage,
}: InputContainerProps) {
  const [inputText, setInputText] = useState<string>("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      if (functionToVerify !== null || isResponseFetching) {
        textareaRef.current.blur();
        return;
      }
      textareaRef.current.focus();
    }
  }, [functionToVerify, isResponseFetching]);

  const handleSendMessage = () => {
    const trimmedInputText: string = inputText.trim();
    setInputText("");
    sendMessage(trimmedInputText);
  };

  const canSendMessage = () => {
    return (
      inputText.trim().length > 0 && !isResponseFetching && !isApiKeyLoading
    );
  };

  const isTextAreaDisabled = () => {
    return isResponseFetching || functionToVerify !== null;
  };

  useEffect(() => {
    const handleKeyDown = async (event: KeyboardEvent) => {
      if (
        event.key === "Enter" &&
        document.activeElement?.id === "input-text-area"
      ) {
        event.preventDefault();
        handleSendMessage();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [inputText]);

  return (
    <>
      <Textarea
        id="input-text-area"
        ref={textareaRef}
        className="border-2 rounded resize-none max-h-[300px] overflow-auto"
        value={inputText}
        disabled={isTextAreaDisabled()}
        placeholder={isTextAreaDisabled() ? "" : "Type a message..."}
        rows={1}
        onInput={(e) => {
          const target = e.target as HTMLTextAreaElement;
          target.style.height = "auto";
          target.style.height = `${target.scrollHeight}px`;
        }}
        onChange={(e) => setInputText(e.target.value)}
      />
      {isResponseFetching && (
        <div className="absolute inset-0 flex items-center justify-center">
          <Loader />
        </div>
      )}
      <VerificationOption
        isEnabled={functionToVerify !== null}
        sendMessage={sendMessage}
      />
      <Button
        id="send-btn"
        className={`${canSendMessage() ? "animate-bounce" : ""}`}
        disabled={!canSendMessage()}
        onClick={(e) => {
          e.preventDefault();
          handleSendMessage();
        }}
      >
        Send
      </Button>
    </>
  );
}
