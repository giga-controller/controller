"use server";

import {
  LoginRequest,
  loginResponseSchema,
  LoginResponse,
} from "@/types/actions/user/login";

import axios from "axios";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
const SERVICE_ENDPOINT = "api/user/login";

export async function login(input: LoginRequest): Promise<LoginResponse> {
  try {
    const response = await axios.post(
      `${BACKEND_URL}/${SERVICE_ENDPOINT}`,
      input,
    );
    const loginResponse = loginResponseSchema.parse(response.data);

    return loginResponse;
  } catch (error) {
    console.error(error);
    throw error;
  }
}
