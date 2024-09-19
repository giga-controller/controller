import React from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ScrollBar } from "@/components/ui/scroll-area";
import { Message, roleSchema } from "@/types/actions/query/base";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import ReactMarkdown from "react-markdown";
import Loader from "react-loaders";
import "loaders.css/src/animations/ball-pulse.scss";
import { Button } from "@/components/ui/button";

type ChatContainerProps = {
  chatHistory: Message[];
  profileImageUrl: string;
  fallbackCharacter: string;
  isResponseFetching: boolean;
  functionToVerify: string | null;
  updateChatHistory: (newChatHistory: Message[]) => void;
};

export default function ChatContainer({
  chatHistory,
  profileImageUrl,
  fallbackCharacter,
  isResponseFetching,
  functionToVerify,
  updateChatHistory,
}: ChatContainerProps) {
  const handleDelete = (index: number) => {
    updateChatHistory(chatHistory.filter((_, i) => i < index));
  };

  const renderMessageData = (message: Message, isLastMessage: boolean) => {
    if (!message.data || message.data.length === 0) {
      return null;
    }

    let visibleColumns = Object.keys(message.data[0]);

    // Remove confusing null values from the confirmation request table
    if (isLastMessage && functionToVerify !== null) {
      visibleColumns = visibleColumns.filter(
        (key) => message.data![message.data!.length - 1][key] !== null,
      );
    }

    return (
      <div className="relative mt-2 w-full max-w-screen-lg overflow-auto">
        <Table className="w-full">
          <TableHeader>
            <TableRow>
              {visibleColumns.map((key) => (
                <TableHead
                  key={key}
                  className="text-left text-gray-500 font-normal text-sm px-4 py-2 whitespace-nowrap"
                >
                  {key.toLowerCase()}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {message.data.map((row, rowIndex) => (
              <TableRow key={rowIndex}>
                {visibleColumns.map((key, cellIndex) => (
                  <TableCell
                    key={cellIndex}
                    className="px-4 py-2 whitespace-nowrap"
                  >
                    <ReactMarkdown
                      components={{
                        a: ({ node, ...props }) => (
                          <a {...props} className="text-blue-500 underline" />
                        ),
                      }}
                    >
                      {typeof row[key] === "object"
                        ? JSON.stringify(row[key])
                        : String(row[key])}
                    </ReactMarkdown>
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <ScrollBar orientation="horizontal" />
      </div>
    );
  };

  return (
    <div className="pt-6">
      {chatHistory.map((message: Message, index: number) => (
        <div key={index}>
          <div
            className={`flex items-start mb-4 ${
              message.role === roleSchema.Values.user
                ? "justify-end"
                : "justify-start"
            }`}
          >
            {message.role === roleSchema.Values.assistant && (
              <Avatar className="mr-2">
                <AvatarImage src="/path/to/assistant-avatar.png" />
                <AvatarFallback>AI</AvatarFallback>
              </Avatar>
            )}
            <div
              className={`relative p-4 rounded-lg ${
                message.role === roleSchema.Values.user
                  ? "bg-blue-500 dark:bg-blue-800 text-white"
                  : "bg-gray-300 dark:bg-gray-400 text-black"
              }`}
            >
              {message.role === roleSchema.Values.user && (
                <Button
                  className="absolute top-2 right-2 bg-transparent border-none p-0 size-2 text-white hover:bg-transparent"
                  onClick={() => handleDelete(index)}
                >
                  x
                </Button>
              )}
              <ReactMarkdown
                components={{
                  a: ({ node, ...props }) => (
                    <a {...props} className="text-blue-500 underline" />
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
              {renderMessageData(message, index === chatHistory.length - 1)}
            </div>
            {message.role === roleSchema.Values.user && (
              <Avatar className="ml-2">
                <AvatarImage src={profileImageUrl} />
                <AvatarFallback>{fallbackCharacter}</AvatarFallback>
              </Avatar>
            )}
          </div>
        </div>
      ))}
      {isResponseFetching && (
        <div className="flex items-start mb-4 justify-start">
          <Avatar className="mr-2">
            <AvatarImage src="/path/to/assistant-avatar.png" />
            <AvatarFallback>AI</AvatarFallback>
          </Avatar>
          <div className="p-2 rounded-lg bg-gray-300 text-black">
            <Loader type="ball-pulse" active={true} />
          </div>
        </div>
      )}
    </div>
  );
}
