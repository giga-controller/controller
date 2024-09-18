import { toast } from "@/components/ui/use-toast";
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function handleCopy(text: string, targetName: string) {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      toast({
        title: "Copied to clipboard",
        description: `The ${targetName} has been copied to your clipboard.`,
        duration: 3000,
      });
    })
    .catch((err) => {
      // eslint-disable-next-line no-console
      console.error("Failed to copy text: ", err);
      toast({
        title: "Copy failed",
        description: `Failed to copy the ${targetName}. Please try again.`,
        variant: "destructive",
        duration: 3000,
      });
    });
}

export function capitaliseFirstLetter(string: string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

export function extractJsonAndText(input: string): string[] {
  const result: string[] = [];
  let currentIndex = 0;
  let inBrackets = 0;
  let inBraces = 0;
  let start = 0;

  for (let i = 0; i < input.length; i++) {
    const char = input[i];

    if (char === "[") {
      if (inBrackets === 0 && inBraces === 0) {
        if (i > currentIndex) {
          result.push(input.slice(currentIndex, i).trim());
        }
        start = i;
      }
      inBrackets++;
    } else if (char === "]") {
      inBrackets--;
      if (inBrackets === 0 && inBraces === 0) {
        result.push(input.slice(start, i + 1));
        currentIndex = i + 1;
      }
    } else if (char === "{") {
      if (inBrackets === 0 && inBraces === 0) {
        if (i > currentIndex) {
          result.push(input.slice(currentIndex, i).trim());
        }
        start = i;
      }
      inBraces++;
    } else if (char === "}") {
      inBraces--;
      if (inBrackets === 0 && inBraces === 0) {
        result.push(input.slice(start, i + 1));
        currentIndex = i + 1;
      }
    }
  }

  // Add any remaining text after the last JSON object or array
  if (currentIndex < input.length) {
    result.push(input.slice(currentIndex).trim());
  }

  return result.filter((item) => item !== "");
}
