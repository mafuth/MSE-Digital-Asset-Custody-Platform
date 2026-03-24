<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { createChart, ColorType, AreaSeries, type IChartApi, type ISeriesApi } from 'lightweight-charts';

	let { data = [] } = $props();
	let chartContainer = $state<HTMLDivElement>();
	let chart: IChartApi;
	let areaSeries: ISeriesApi<"Area">;

	function initChart() {
		if (!chartContainer) return;

		chart = createChart(chartContainer, {
			layout: {
				background: { type: ColorType.Solid, color: 'transparent' },
				textColor: '#64748b',
				fontSize: 12,
				fontFamily: 'Inter, sans-serif',
			},
			grid: {
				vertLines: { color: 'rgba(226, 232, 240, 0.5)' },
				horzLines: { color: 'rgba(226, 232, 240, 0.5)' },
			},
			width: chartContainer.clientWidth,
			height: chartContainer.clientHeight || 400,
			rightPriceScale: {
				borderVisible: false,
				scaleMargins: {
					top: 0.1,
					bottom: 0.1,
				},
			},
			timeScale: {
				borderVisible: false,
				timeVisible: true,
				secondsVisible: false,
			},
			handleScroll: true,
			handleScale: true,
			crosshair: {
				horzLine: {
					visible: true,
					labelVisible: true,
				},
				vertLine: {
					visible: true,
					labelVisible: true,
				},
			},
		});

		// Universal series creation API for v5.x
		areaSeries = chart.addSeries(AreaSeries, {
			lineColor: '#0f172a',
			topColor: 'rgba(15, 23, 42, 0.1)',
			bottomColor: 'rgba(15, 23, 42, 0.0)',
			lineWidth: 2,
			priceFormat: {
				type: 'price',
				precision: 2,
				minMove: 0.01,
			},
		});

		if (areaSeries && data.length > 0) {
			areaSeries.setData(data);
			chart.timeScale().fitContent();
		}
	}

	$effect(() => {
		if (areaSeries && data.length > 0) {
			areaSeries.setData(data);
			chart.timeScale().fitContent();
		}
	});

	onMount(() => {
		initChart();
		const handleResize = () => {
			if (chart && chartContainer) {
				chart.applyOptions({
					width: chartContainer.clientWidth,
					height: chartContainer.clientHeight,
				});
			}
		};
		window.addEventListener('resize', handleResize);
		return () => window.removeEventListener('resize', handleResize);
	});

	onDestroy(() => {
		if (chart) chart.remove();
	});
</script>

<div bind:this={chartContainer} class="w-full h-full min-h-[400px]"></div>
