import {
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Copy } from "lucide-react";
import { useEffect, useState } from "react";
import { handleCopy } from "@/lib/utils";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { tokenGetRequestSchema } from "@/types/actions/token";
import { isUserAuthenticated } from "@/actions/token";
import { queryClient } from "@/components/shared/query-provider";
import { INTEGRATION_AUTH_STATUS_QUERY_KEY } from "@/constants/keys";
import Link from "next/link";
import { ROUTE } from "@/constants/route";

const BASE_URL = process.env.NEXT_PUBLIC_DEFAULT_SITE_URL;

type AuthDialogContentProps = {
  name: string;
  apiKey: string;
  loginBase: string;
  exchangeBase: string;
  scope: string;
  verifierRequired?: boolean;
};

export default function AuthDialogContent({
  name,
  apiKey,
  loginBase,
  exchangeBase,
  scope,
  verifierRequired = true,
}: AuthDialogContentProps) {
  const router = useRouter();
  const [oauthRedirectUrl] = useState<string>(
    `${BASE_URL}/api/oauth2/callback`,
  );
  const [clientId, setClientId] = useState<string>("");
  const [clientSecret, setClientSecret] = useState<string>("");
  const [oauthUrl, setOauthUrl] = useState<string>("");

  const { data, isLoading } = useQuery({
    queryKey: [INTEGRATION_AUTH_STATUS_QUERY_KEY(name), apiKey],
    queryFn: async () => {
      if (!apiKey) {
        return false;
      }
      const parsedTokenGetRequest = tokenGetRequestSchema.parse({
        api_key: apiKey,
        table_name: name.toLowerCase(),
      });
      const response = await isUserAuthenticated(parsedTokenGetRequest);
      return response.is_authenticated;
    },
    staleTime: 15 * 60 * 1000,
    refetchInterval: 15 * 60 * 1000,
    refetchOnWindowFocus: false,
  });

  const invalidateAuthCache = () => {
    queryClient.invalidateQueries({ queryKey: [`is${name}Authenticated`] });
  };

  useEffect(() => {
    function generateRandomString(length: number): string {
      const array = new Uint8Array(length);
      crypto.getRandomValues(array);
      return Array.from(array, (byte) =>
        byte.toString(16).padStart(2, "0"),
      ).join("");
    }

    async function sha256(plain: string): Promise<ArrayBuffer> {
      const encoder = new TextEncoder();
      const encrypted = encoder.encode(plain);
      return await crypto.subtle.digest("SHA-256", encrypted);
    }

    function base64UrlEncode(buffer: ArrayBuffer): string {
      const bytes = new Uint8Array(buffer);
      let binary = "";
      for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
      }
      return btoa(binary)
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/, "");
    }

    const codeVerifier = generateRandomString(128);
    sha256(codeVerifier).then((hash) => {
      const codeChallenge = base64UrlEncode(hash);
      setOauthUrl(
        `/api/oauth2/login?clientId=${clientId}&clientSecret=${clientSecret}&scope=${scope}&controllerApiKey=${apiKey}&tableName=${name.toLowerCase()}&loginBase=${loginBase}&exchangeBase=${exchangeBase}&redirect_uri=${`${process.env.NEXT_PUBLIC_DEFAULT_SITE_URL}/api/oauth2/callback`}&code_verifier=${codeVerifier}&code_challenge=${codeChallenge}&code_challenge_method=S256&verifierRequired=${verifierRequired}`,
      );
    });
  }, [clientId, clientSecret, apiKey, scope, name, loginBase, exchangeBase]);

  const isButtonVisible = clientId !== "" && clientSecret !== "";

  return (
    <DialogHeader>
      <div className="flex flex-row items-center justify-between space-x-3 mr-4 pb-2">
        <DialogTitle>{name}</DialogTitle>
        <Link
          href={ROUTE[name]}
          className="px-3 rounded-md text-sm underline text-blue-700 dark:text-blue-300"
        >
          Help
        </Link>
      </div>
      <DialogDescription>OAuth Redirect URL</DialogDescription>
      <div className="flex items-center space-x-2">
        <Input
          id="oauth-redirect-url"
          defaultValue={oauthRedirectUrl}
          readOnly
        />
        <Button size="sm" className="px-3">
          <Copy
            className="h-4 w-4"
            onClick={() => handleCopy(oauthRedirectUrl, "url")}
          />
        </Button>
      </div>
      <DialogDescription>Client ID</DialogDescription>
      <Input
        id="client-id"
        value={clientId}
        onChange={(e) => setClientId(e.target.value)}
      />
      <DialogDescription>Client Secret</DialogDescription>
      <Input
        id="client-secret"
        value={clientSecret}
        onChange={(e) => setClientSecret(e.target.value)}
      />
      <Button
        className={`mt-2 ${isButtonVisible ? "" : "invisible pointer-events-none"}`}
        onClick={() => {
          invalidateAuthCache();
          router.push(oauthUrl);
        }}
      >
        Login with {name}
      </Button>
    </DialogHeader>
  );
}
