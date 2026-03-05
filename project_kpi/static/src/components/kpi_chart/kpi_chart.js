/** @odoo-module **/

import { Component, onWillStart, onMounted, onWillUnmount, useRef, onPatched } from "@odoo/owl";
import { loadJS } from "@web/core/assets";

export class KpiChart extends Component {
    static template = "project_kpi.KpiChart";
    static props = {
        title: String,
        type: String, 
        data: { type: Object, optional: true } 
    };

    setup() {
        this.canvasRef = useRef("chartCanvas");
        this.chartInstance = null;

        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
        });

        onMounted(() => {
            this.renderChart();
        });

        onPatched(() => {
            this.renderChart();
        });

        onWillUnmount(() => {
            if (this.chartInstance) {
                this.chartInstance.destroy();
            }
        });
    }

    renderChart() {
        if (this.chartInstance) {
            this.chartInstance.destroy();
        }
        if (!this.canvasRef.el) {
            return;
        }

        const ctx = this.canvasRef.el.getContext("2d");
        const chartData = this.props.data || { labels: [], datasets: [] };
        this.chartInstance = new window.Chart(ctx, {
            type: this.props.type,
            data: this.props.data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    position: 'bottom',
                },
                scales: this.props.type === 'bar' ? {
                    yAxes: [{ ticks: { beginAtZero: true } }]
                } : {}
            }
        });
    }
}