"use server";

import {
  TokenGetRequest,
  tokenGetResponseSchema,
  TokenGetResponse,
} from "@/types/actions/token";

import axios from "axios";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
const SERVICE_ENDPOINT = "api/token";

export async function isUserAuthenticated(
  input: TokenGetRequest,
): Promise<TokenGetResponse> {
  try {
    const response = await axios.get(`${BACKEND_URL}/${SERVICE_ENDPOINT}`, {
      params: input,
    });
    const tokenResponse = tokenGetResponseSchema.parse(response.data);

    return tokenResponse;
  } catch (error) {
    console.error(error);
    throw error;
  }
}
