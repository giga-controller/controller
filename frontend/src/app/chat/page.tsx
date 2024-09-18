"use client";

import IntegrationAuth from "@/components/integration-auth";
import { integrationEnum } from "@/types/integration";
import ApiKey from "@/components/api-key";
import { useState } from "react";
import { Integration } from "@/types/integration";

export default function HomePage() {
  const [apiKey, setApiKey] = useState<string>("");
  const updateApiKey = (newApiKey: string) => {
    setApiKey(newApiKey);
  };

  return (
    <>
      <div className="flex flex-col m-4 max-w-[500px] mx-auto">
        <ApiKey apiKey={apiKey} updateApiKey={updateApiKey} />
      </div>
      <div className="grid grid-cols-4 gap-4 p-4 max-w-[1000px] mx-auto">
        {Object.values(integrationEnum.Values).map((integration) => (
          <IntegrationAuth
            key={`${integration}_icon`}
            integration={integration as Integration}
            apiKey={apiKey ?? ""}
          />
        ))}
      </div>
    </>
  );
}
