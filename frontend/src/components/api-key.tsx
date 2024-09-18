import { Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@radix-ui/react-label";
import { useCallback, useMemo } from "react";
import Shimmer from "@/components/accessory/shimmer";
import { Input } from "@/components/ui/input";
import { login } from "@/actions/user/login";
import { loginRequestSchema } from "@/types/actions/user/login";
import { useQuery } from "@tanstack/react-query";
import { useUser } from "@clerk/nextjs";
import { API_KEY_QUERY_KEY } from "@/constants/keys";
import { handleCopy } from "@/lib/utils";

type ApiKeyProps = {
  apiKey: string;
  updateApiKey: (apiKey: string) => void;
};

export default function ApiKey({ apiKey, updateApiKey }: ApiKeyProps) {
  const { user, isLoaded } = useUser();
  const { isLoading } = useQuery({
    queryKey: [API_KEY_QUERY_KEY, user?.id],
    queryFn: async () => {
      if (!isLoaded || !user) {
        return null;
      }
      const parsedLoginRequest = loginRequestSchema.parse({
        id: user.id,
        name: user.firstName,
        email: user.primaryEmailAddress?.emailAddress,
      });
      const response = await login(parsedLoginRequest);
      updateApiKey(response.api_key);
    },
    enabled: isLoaded && !!user,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
  const copyApiKey = useCallback(() => {
    if (apiKey) {
      handleCopy(apiKey, API_KEY_QUERY_KEY);
    }
  }, [apiKey]);
  const maskedApiKey = useMemo(() => {
    if (!apiKey) {
      return "";
    }

    return `${apiKey.slice(0, 4)}${"*".repeat(apiKey.length - 4)}`;
  }, [apiKey]);

  return (
    <>
      <Label htmlFor="api-key" className="mb-1">
        API Key
      </Label>
      <div className="flex space-x-3">
        {isLoading ? <Shimmer /> : <Input id="api-key" value={maskedApiKey} />}
        <Button size="sm" className="px-3">
          <Copy className="h-4 w-4" onClick={copyApiKey} />
        </Button>
      </div>
    </>
  );
}
