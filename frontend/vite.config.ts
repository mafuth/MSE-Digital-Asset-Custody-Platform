import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	ssr: {
		noExternal: ["bits-ui"],
	},
	server: {
		proxy: {
			"/api": {
				target: "http://192.168.18.83:8000",
				changeOrigin: true,
			},
		},
	},
});
