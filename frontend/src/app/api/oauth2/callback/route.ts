import axios from "axios";
import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { tokenPostRequestSchema } from "@/types/api/token";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);

  const state = searchParams.get("state");
  const storedState = cookies().get("authState")?.value;
  const storedClientId = cookies().get("clientId")?.value;
  const storedClientSecret = cookies().get("clientSecret")?.value;
  const storedControllerApiKey = cookies().get("controllerApiKey")?.value;
  const storedExchangeBase = cookies().get("exchangeBase")?.value || "";
  const storedTableName = cookies().get("tableName")?.value;
  const storedRedirectUri = cookies().get("redirect_uri")?.value;
  const storedCodeVerifier = cookies().get("code_verifier")?.value;
  const storedVerifierRequired = cookies().get("verifierRequired")?.value;

  if (!state || state !== storedState) {
    return NextResponse.json(
      { error: "Invalid state parameter" },
      { status: 400 },
    );
  }

  cookies().delete("authState");

  const code = searchParams.get("code");

  if (!code) {
    return NextResponse.json(
      { error: "Authorization code is missing" },
      { status: 400 },
    );
  }

  try {
    const params = new URLSearchParams();

    params.append("code", code);
    params.append("redirect_uri", storedRedirectUri as string);
    params.append("grant_type", "authorization_code");
    if (storedVerifierRequired === "true") {
      params.append("code_verifier", storedCodeVerifier as string);
    }

    const credentials = btoa(`${storedClientId}:${storedClientSecret}`);

    console.log("STORED EXCHANGE BASE");
    console.log(storedExchangeBase);

    const response = await axios.post(storedExchangeBase, params, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        Authorization: `Basic ${credentials}`,
      },
    });

    console.log("RESPONSE");
    console.log(response);

    const tokenData = response.data;
    const accessToken: string = tokenData.access_token;
    const refreshToken: string | null = tokenData.refresh_token || null;

    console.log("TOKEN DATA");
    console.log(tokenData);

    const parsedTokenRequest = tokenPostRequestSchema.parse({
      api_key: storedControllerApiKey,
      access_token: accessToken,
      refresh_token: refreshToken,
      client_id: storedClientId,
      client_secret: storedClientSecret,
      table_name: storedTableName,
    });

    console.log("PARSED TOKEN REQUEST");
    console.log(parsedTokenRequest);

    await axios.post(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/token`,
      parsedTokenRequest,
    );

    console.log("BACKEND REQUEST COMPLETED");

    return NextResponse.redirect(`${process.env.NEXT_PUBLIC_DEFAULT_SITE_URL}`);
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error(
        "Token exchange error:",
        error.response?.data || error.message,
      );
    } else {
      console.error("Token exchange error:", error);
    }

    return NextResponse.json(
      { error: "Failed to retrieve access token" },
      { status: 500 },
    );
  }
}
