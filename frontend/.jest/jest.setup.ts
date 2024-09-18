import "@testing-library/jest-dom";
import fetchMock from "jest-fetch-mock";

// Mock ResizeObserver
class ResizeObserver {
  observe() {
    // do nothing
  }
  unobserve() {
    // do nothing
  }
  disconnect() {
    // do nothing
  }
}

global.ResizeObserver = ResizeObserver;
fetchMock.enableMocks();
