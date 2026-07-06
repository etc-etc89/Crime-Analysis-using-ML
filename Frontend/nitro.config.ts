import { defineNitroConfig } from "nitropack/config";

export default defineNitroConfig({
  output: {
    dir: 'dist',
    serverDir: 'dist/server',
    publicDir: 'dist/public'
  }
});
