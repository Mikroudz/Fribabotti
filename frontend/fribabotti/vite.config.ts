import { defineConfig, loadEnv } from 'vite'
import { devtools } from '@tanstack/devtools-vite'

import { tanstackRouter } from "@tanstack/router-plugin/vite";
import basicSsl from "@vitejs/plugin-basic-ssl";

import viteReact from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const config = defineConfig(({mode}) => {
    
    const env = loadEnv(mode, process.cwd(), '')
    
    return {
        base: env.VITE_BASE_PATH || '/', 
        resolve: { tsconfigPaths: true },
        plugins: [tanstackRouter({ target: "react", autoCodeSplitting: true }), devtools(), tailwindcss(),  viteReact(), basicSsl(),],
        server: {
                host: "0.0.0.0",
                proxy: {
                    "/api/v1": {
                        target: "http://127.0.0.1:8000",
                        changeOrigin: true,
                        secure: false,
                        rewrite: (path) => path.replace("http", "https"),
                    },
                },
            },
build: {
            rollupOptions: {
                output: {
                    // Force recharts into its own chunk to prevent tree-shaking mangling
                    manualChunks: (id) => {
                        if (id.includes('node_modules/recharts') || id.includes('node_modules/d3') || id.includes('node_modules/react-smooth')) {
                            return 'vendor-recharts';
                        }
                    }
                }
            }
        },
        optimizeDeps: {
            include: ['recharts']
        }
}})

export default config
